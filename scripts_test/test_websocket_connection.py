"""
Test WebSocket connection to Polymarket CLOB API
Diagnose connection issues and test different subscription methods
"""

import os
import sys
import time
import json
import websocket
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test configuration
WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
TEST_MARKET_ID = "929488"  # BTC 15-min market from logs

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def log_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def log_error(msg):
    print(f"{RED}✗ {msg}{RESET}")

def log_info(msg):
    print(f"{BLUE}ℹ {msg}{RESET}")

def log_warning(msg):
    print(f"{YELLOW}⚠ {msg}{RESET}")


class WebSocketTester:
    def __init__(self):
        self.messages_received = []
        self.connected = False
        self.connection_opened = False
        self.connection_closed = False
        self.error_count = 0

    def on_message(self, ws, message):
        """Handle incoming WebSocket message"""
        log_success(f"Message received: {message[:200]}...")
        self.messages_received.append(message)

        try:
            data = json.loads(message)
            log_info(f"Message type: {data.get('type', 'unknown')}")
            log_info(f"Full message: {json.dumps(data, indent=2)}")
        except json.JSONDecodeError:
            log_warning(f"Non-JSON message: {message}")

    def on_error(self, ws, error):
        """Handle WebSocket error"""
        log_error(f"WebSocket error: {error}")
        self.error_count += 1

    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        log_warning(f"Connection closed: code={close_status_code}, msg={close_msg}")
        self.connection_closed = True

    def on_open(self, ws):
        """Handle WebSocket open"""
        log_success("WebSocket connection opened!")
        self.connection_opened = True
        self.connected = True

    def test_basic_connection(self):
        """Test 1: Basic connection without subscription"""
        print("\n" + "="*70)
        print("TEST 1: Basic Connection (No Subscription)")
        print("="*70)

        ws = websocket.WebSocketApp(
            WS_URL,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )

        # Run for 5 seconds
        import threading
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()

        time.sleep(5)
        ws.close()

        if self.connection_opened:
            log_success("Connection test passed")
        else:
            log_error("Connection test failed - never opened")

        log_info(f"Messages received: {len(self.messages_received)}")
        log_info(f"Errors encountered: {self.error_count}")

    def test_unauthenticated_subscription(self):
        """Test 2: Unauthenticated subscription"""
        print("\n" + "="*70)
        print("TEST 2: Unauthenticated Subscription")
        print("="*70)

        self.messages_received = []
        self.connection_opened = False

        def on_open_with_sub(ws):
            self.on_open(ws)

            # Send subscription message
            subscription = {
                "type": "subscribe",
                "channel": "market",
                "market": TEST_MARKET_ID
            }

            log_info(f"Sending subscription: {json.dumps(subscription)}")
            ws.send(json.dumps(subscription))

        ws = websocket.WebSocketApp(
            WS_URL,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=on_open_with_sub
        )

        import threading
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()

        time.sleep(10)
        ws.close()

        log_info(f"Messages after subscription: {len(self.messages_received)}")

        if len(self.messages_received) > 0:
            log_success("Received messages after subscription")
        else:
            log_warning("No messages received - may require authentication")

    def test_authenticated_subscription(self):
        """Test 3: Authenticated subscription (if credentials available)"""
        print("\n" + "="*70)
        print("TEST 3: Authenticated Subscription")
        print("="*70)

        api_key = os.getenv("POLYMARKET_API_KEY")
        api_secret = os.getenv("POLYMARKET_API_SECRET")
        api_passphrase = os.getenv("POLYMARKET_API_PASSPHRASE")

        if not all([api_key, api_secret, api_passphrase]):
            log_warning("Skipping - No API credentials in .env")
            log_info("Add POLYMARKET_API_KEY, POLYMARKET_API_SECRET, POLYMARKET_API_PASSPHRASE to .env")
            return

        log_success("Found API credentials!")

        self.messages_received = []
        self.connection_opened = False

        import hmac
        import hashlib
        import base64

        def generate_signature(timestamp, secret):
            """Generate HMAC signature"""
            secret_bytes = base64.b64decode(secret)
            signature = hmac.new(
                secret_bytes,
                timestamp.encode('utf-8'),
                hashlib.sha256
            ).digest()
            return base64.b64encode(signature).decode('utf-8')

        def on_open_with_auth(ws):
            self.on_open(ws)

            timestamp = str(int(time.time()))
            signature = generate_signature(timestamp, api_secret)

            # Send authenticated subscription
            subscription = {
                "type": "subscribe",
                "channel": "market",
                "market": TEST_MARKET_ID,
                "auth": {
                    "apiKey": api_key,
                    "signature": signature,
                    "timestamp": timestamp,
                    "passphrase": api_passphrase
                }
            }

            log_info(f"Sending authenticated subscription")
            log_info(f"  API Key: {api_key[:8]}...")
            log_info(f"  Timestamp: {timestamp}")
            ws.send(json.dumps(subscription))

        ws = websocket.WebSocketApp(
            WS_URL,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=on_open_with_auth
        )

        import threading
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()

        time.sleep(10)
        ws.close()

        log_info(f"Messages with auth: {len(self.messages_received)}")

        if len(self.messages_received) > 0:
            log_success("Authenticated subscription successful!")
        else:
            log_error("Authenticated subscription failed - no messages")

    def test_orderbook_subscription(self):
        """Test 4: Orderbook data subscription"""
        print("\n" + "="*70)
        print("TEST 4: Orderbook Subscription")
        print("="*70)

        self.messages_received = []
        self.connection_opened = False

        def on_open_orderbook(ws):
            self.on_open(ws)

            # Try subscribing to orderbook
            subscription = {
                "type": "subscribe",
                "channel": "orderbook",
                "market": TEST_MARKET_ID
            }

            log_info(f"Sending orderbook subscription: {json.dumps(subscription)}")
            ws.send(json.dumps(subscription))

        ws = websocket.WebSocketApp(
            WS_URL,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=on_open_orderbook
        )

        import threading
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()

        time.sleep(10)
        ws.close()

        log_info(f"Orderbook messages: {len(self.messages_received)}")


def main():
    print("="*70)
    print("Polymarket WebSocket Connection Tester")
    print("="*70)
    print(f"Target: {WS_URL}")
    print(f"Test Market ID: {TEST_MARKET_ID}")
    print("="*70)

    tester = WebSocketTester()

    # Run all scripts_test
    tester.test_basic_connection()
    time.sleep(2)

    tester.test_unauthenticated_subscription()
    time.sleep(2)

    tester.test_authenticated_subscription()
    time.sleep(2)

    tester.test_orderbook_subscription()

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total messages received: {len(tester.messages_received)}")
    print(f"Total errors: {tester.error_count}")

    if tester.connection_opened:
        log_success("Connection capability: WORKING")
    else:
        log_error("Connection capability: FAILED")

    if len(tester.messages_received) > 0:
        log_success("Message reception: WORKING")
    else:
        log_warning("Message reception: NO MESSAGES (may need auth)")

    print("="*70)
    print("\nRECOMMENDATIONS:")
    print("1. If connection drops immediately: Check if endpoint requires auth")
    print("2. If no messages received: Generate and add API credentials to .env")
    print("3. If errors occur: Check network/firewall settings")
    print("4. See docs/WEBSOCKET_AUTH.md for credential generation")
    print("="*70)


if __name__ == "__main__":
    main()
