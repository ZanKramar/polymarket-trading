"""
WebSocket client for real-time Polymarket price updates with CLOB authentication support
"""

import json
import logging
import threading
import time
import hmac
import hashlib
import base64
from typing import Dict, Optional, Callable
from datetime import datetime
import websocket  # websocket-client library

logger = logging.getLogger(__name__)


class PolymarketWebSocketClient:
    """
    WebSocket client for receiving real-time price updates from Polymarket
    """

    def __init__(
        self,
        on_price_update: Optional[Callable] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        api_passphrase: Optional[str] = None
    ):
        """
        Initialize WebSocket client with optional CLOB authentication

        Args:
            on_price_update: Callback function(market_id, yes_price, no_price)
            api_key: CLOB API key (for authenticated subscriptions)
            api_secret: CLOB API secret (base64-encoded)
            api_passphrase: CLOB API passphrase
        """
        # Option 1: Public WebSocket endpoint for real-time data
        # Falls back to REST API if connection fails
        self.ws_url = "wss://ws-live-data.polymarket.com"
        self.ws = None
        self.subscribed_markets = set()
        self.price_cache: Dict[str, Dict[str, float]] = {}  # market_id -> {yes_price, no_price}
        self.orderbook_cache: Dict[str, Dict[str, list]] = {}  # market_id -> {bids: [...], asks: [...]}
        self.on_price_update = on_price_update
        self.running = False
        self.thread = None
        self.reconnect_delay = 5  # seconds

        # Authentication credentials
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.authenticated = all([api_key, api_secret, api_passphrase])

        if self.authenticated:
            logger.info("WebSocket client initialized with authentication")
        else:
            logger.info("WebSocket client initialized without authentication (limited functionality)")

    def connect(self):
        """Connect to the WebSocket and start listening"""
        if self.running:
            logger.warning("WebSocket already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_forever, daemon=True)
        self.thread.start()
        logger.info("WebSocket client started")

    def _run_forever(self):
        """Run the WebSocket connection with auto-reconnect"""
        while self.running:
            try:
                logger.info(f"Connecting to WebSocket: {self.ws_url}")

                self.ws = websocket.WebSocketApp(
                    self.ws_url,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close,
                    on_open=self._on_open
                )

                # Run forever with ping/pong to keep connection alive
                self.ws.run_forever(ping_interval=30, ping_timeout=10)

            except Exception as e:
                logger.error(f"WebSocket error: {e}")

            if self.running:
                logger.info(f"Reconnecting in {self.reconnect_delay} seconds...")
                time.sleep(self.reconnect_delay)

    def _on_open(self, ws):
        """Handle WebSocket connection opened"""
        logger.info("WebSocket connection opened")

        # Resubscribe to all markets
        if self.subscribed_markets:
            logger.info(f"Resubscribing to {len(self.subscribed_markets)} markets")
            for market_id in self.subscribed_markets:
                self._send_subscription(market_id)

    def _on_message(self, ws, message):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)

            # Different message types from Polymarket
            msg_type = data.get('type')

            if msg_type == 'book':
                # Order book update
                market_id = data.get('market')
                asset_id = data.get('asset_id')

                # Extract best bid/ask from order book
                bids = data.get('bids', [])
                asks = data.get('asks', [])

                # Store full orderbook
                if market_id not in self.orderbook_cache:
                    self.orderbook_cache[market_id] = {}

                # Store bids and asks for this asset_id
                asset_key = 'YES' if asset_id else 'NO'  # Simplified - may need better logic
                self.orderbook_cache[market_id][asset_key] = {
                    'bids': bids,
                    'asks': asks,
                    'last_update': datetime.utcnow()
                }

                if bids and asks:
                    best_bid = float(bids[0]['price']) if bids else 0.0
                    best_ask = float(asks[0]['price']) if asks else 0.0

                    # Update price cache
                    if market_id not in self.price_cache:
                        self.price_cache[market_id] = {}

                    # For BTC markets, asset_id determines if it's YES (UP) or NO (DOWN)
                    # Store both and calculate mid-price
                    mid_price = (best_bid + best_ask) / 2 if best_bid and best_ask else 0.0

                    # Update cache
                    self.price_cache[market_id]['mid_price'] = mid_price
                    self.price_cache[market_id]['best_bid'] = best_bid
                    self.price_cache[market_id]['best_ask'] = best_ask
                    self.price_cache[market_id]['spread'] = best_ask - best_bid
                    self.price_cache[market_id]['last_update'] = datetime.utcnow()

                    # Call callback if provided
                    if self.on_price_update:
                        # For now, assume 50/50 split - in reality we'd need to track both assets
                        self.on_price_update(market_id, mid_price, 1.0 - mid_price)

            elif msg_type == 'trade':
                # Trade executed - also update prices
                market_id = data.get('market')
                price = float(data.get('price', 0))

                if market_id and price:
                    if market_id not in self.price_cache:
                        self.price_cache[market_id] = {}

                    self.price_cache[market_id]['last_trade'] = price
                    self.price_cache[market_id]['last_update'] = datetime.utcnow()

        except json.JSONDecodeError:
            logger.debug(f"Could not parse message: {message}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def _on_error(self, ws, error):
        """Handle WebSocket error"""
        logger.error(f"WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection closed"""
        logger.info(f"WebSocket connection closed: {close_status_code} - {close_msg}")

    def subscribe(self, market_id: str, asset_ids: list = None):
        """
        Subscribe to price updates for a market

        Args:
            market_id: Market ID to subscribe to
            asset_ids: Optional list of asset IDs (for YES/NO tokens)
        """
        if market_id in self.subscribed_markets:
            return

        self.subscribed_markets.add(market_id)

        if self.ws and self.ws.sock and self.ws.sock.connected:
            self._send_subscription(market_id, asset_ids)

    def _generate_signature(self, timestamp: str) -> str:
        """
        Generate HMAC-SHA256 signature for WebSocket authentication

        Args:
            timestamp: Unix timestamp as string

        Returns:
            Base64-encoded signature
        """
        if not self.api_secret:
            return ""

        try:
            # Decode base64 secret
            secret_bytes = base64.b64decode(self.api_secret)

            # Create message to sign (for WebSocket, typically just the timestamp)
            message = timestamp

            # Generate HMAC signature
            signature = hmac.new(
                secret_bytes,
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()

            # Return base64-encoded signature
            return base64.b64encode(signature).decode('utf-8')

        except Exception as e:
            logger.error(f"Failed to generate signature: {e}")
            return ""

    def _send_subscription(self, market_id: str, asset_ids: list = None):
        """Send subscription message to WebSocket with optional authentication"""
        try:
            # Polymarket WebSocket subscription format
            subscription_message = {
                "type": "subscribe",
                "channel": "market",
                "market": market_id
            }

            if asset_ids:
                subscription_message["assets"] = asset_ids

            # Add authentication if credentials available
            if self.authenticated:
                timestamp = str(int(time.time()))
                signature = self._generate_signature(timestamp)

                subscription_message["auth"] = {
                    "apiKey": self.api_key,
                    "signature": signature,
                    "timestamp": timestamp,
                    "passphrase": self.api_passphrase
                }

                logger.debug(f"Sending authenticated subscription to market: {market_id}")
            else:
                logger.debug(f"Sending unauthenticated subscription to market: {market_id}")

            self.ws.send(json.dumps(subscription_message))

        except Exception as e:
            logger.error(f"Failed to send subscription: {e}")

    def unsubscribe(self, market_id: str):
        """
        Unsubscribe from price updates for a market

        Args:
            market_id: Market ID to unsubscribe from
        """
        if market_id not in self.subscribed_markets:
            return

        self.subscribed_markets.remove(market_id)

        if self.ws and self.ws.sock and self.ws.sock.connected:
            try:
                unsubscribe_message = {
                    "type": "unsubscribe",
                    "channel": "market",
                    "market": market_id
                }
                self.ws.send(json.dumps(unsubscribe_message))
                logger.debug(f"Unsubscribed from market: {market_id}")
            except Exception as e:
                logger.error(f"Failed to unsubscribe: {e}")

    def get_price(self, market_id: str) -> Optional[Dict[str, float]]:
        """
        Get latest cached price for a market

        Args:
            market_id: Market ID

        Returns:
            Dictionary with price info or None
        """
        return self.price_cache.get(market_id)

    def get_orderbook(self, market_id: str) -> Optional[Dict[str, dict]]:
        """
        Get latest cached orderbook for a market

        Args:
            market_id: Market ID

        Returns:
            Dictionary with orderbook data: {
                'YES': {'bids': [...], 'asks': [...], 'last_update': ...},
                'NO': {'bids': [...], 'asks': [...], 'last_update': ...}
            } or None
        """
        return self.orderbook_cache.get(market_id)

    def stop(self):
        """Stop the WebSocket client"""
        logger.info("Stopping WebSocket client...")
        self.running = False

        if self.ws:
            self.ws.close()

        if self.thread:
            self.thread.join(timeout=5)

        logger.info("WebSocket client stopped")


# Simplified WebSocket for polling-based approach
class SimpleWebSocketClient:
    """
    Simplified WebSocket client that works in polling mode
    without actual WebSocket connection (fallback)
    """

    def __init__(self):
        logger.info("Using SimpleWebSocketClient (polling mode)")
        self.active = False

    def connect(self):
        self.active = True
        logger.info("SimpleWebSocketClient connected (no-op)")

    def subscribe(self, market_id: str, asset_ids: list = None):
        logger.debug(f"SimpleWebSocketClient subscribe (no-op): {market_id}")

    def unsubscribe(self, market_id: str):
        logger.debug(f"SimpleWebSocketClient unsubscribe (no-op): {market_id}")

    def get_price(self, market_id: str) -> Optional[Dict[str, float]]:
        return None

    def stop(self):
        self.active = False
        logger.info("SimpleWebSocketClient stopped (no-op)")
