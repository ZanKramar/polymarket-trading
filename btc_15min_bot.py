#!/usr/bin/env python3
"""
Bitcoin 15-Minute Trading Bot
Specialized bot for BTC UP/DOWN 15-minute markets
"""

import logging
import sys
import time
from datetime import datetime
from typing import List
from dotenv import load_dotenv

# Load .env BEFORE importing Config
load_dotenv()

from config import Config
from polymarket_client import PolymarketClient
from position_tracker import PositionTracker
from strategies.base_strategy import BaseStrategy, Market, TradeSignal
from websocket_client import PolymarketWebSocketClient
from strategies.btc_15min_strategies import (
    PriceArbitrageStrategy,
    MeanReversionStrategy,
    SimpleBalancedStrategy,
    MomentumStrategy,
    VolumeSpikeStrategy,
    TimeBasedStrategy
)

logger = logging.getLogger(__name__)


class BTC15MinBot:
    """Trading bot specialized for Bitcoin 15-minute markets"""

    def __init__(
        self,
        client: PolymarketClient,
        strategies: List[BaseStrategy],
        check_interval: int = 30,  # Check more frequently (30 seconds)
        dry_run: bool = True,
        max_markets: int = 4,  # Focus on next 4 markets
        use_websocket: bool = True,  # Try WebSocket first, fallback to REST if it fails
        websocket_timeout: int = 10  # Seconds to wait for WebSocket before falling back
    ):
        self.client = client
        self.strategies = strategies
        self.check_interval = check_interval
        self.dry_run = dry_run
        self.max_markets = max_markets
        self.position_tracker = PositionTracker()
        self.use_websocket = use_websocket
        self.websocket_timeout = websocket_timeout
        self.websocket_healthy = False  # Track if WebSocket is actually working

        # Initialize WebSocket client for real-time price updates
        if use_websocket:
            from config import Config
            self.ws_client = PolymarketWebSocketClient(
                on_price_update=self._on_price_update,
                api_key=Config.POLYMARKET_API_KEY,
                api_secret=Config.POLYMARKET_API_SECRET,
                api_passphrase=Config.POLYMARKET_API_PASSPHRASE
            )
        else:
            self.ws_client = None

        logger.info(f"Initialized BTC 15-Min Bot")
        logger.info(f"  Strategies: {len(strategies)}")
        logger.info(f"  Check interval: {check_interval}s")
        logger.info(f"  Max markets to track: {max_markets}")
        logger.info(f"  Dry run: {dry_run}")
        logger.info(f"  WebSocket: {'Try first (fallback to REST if fails)' if use_websocket else 'Disabled (REST API only)'}")

    def _on_price_update(self, market_id: str, yes_price: float, no_price: float):
        """Callback for WebSocket price updates"""
        # Mark WebSocket as healthy when we receive data
        if not self.websocket_healthy:
            self.websocket_healthy = True
            logger.info("✓ WebSocket connection verified - receiving real-time data")
        logger.debug(f"Price update: {market_id} | UP: ${yes_price:.3f} | DOWN: ${no_price:.3f}")

    def get_btc_15min_markets(self) -> List[Market]:
        """
        Fetch BTC 15-minute markets and return the next N closest to expiry
        """
        # Use the specialized BTC 15-min market fetcher
        # This checks the previous, current, and next max_markets intervals
        btc_markets = self.client.get_btc_15min_markets(num_future_markets=self.max_markets)

        # Sort by time until close (soonest first)
        btc_markets.sort(key=lambda m: m.time_until_close())

        # Take only the next N markets
        selected_markets = btc_markets[:self.max_markets]

        if selected_markets:
            logger.info(f"Found {len(btc_markets)} BTC 15-min markets, tracking {len(selected_markets)}")
            for i, market in enumerate(selected_markets, 1):
                hours_left = market.time_until_close()
                logger.info(f"  {i}. Closes in {hours_left*60:.1f} min | UP: ${market.yes_price:.3f} | DOWN: ${market.no_price:.3f}")
                logger.info(f"      Question: {market.question[:70]}")

                # Subscribe to WebSocket updates for this market
                if self.ws_client:
                    self.ws_client.subscribe(market.id)
        else:
            logger.warning("No BTC 15-min markets found")

        return selected_markets

    def run_once(self) -> int:
        """Run one iteration of the trading bot"""
        logger.info("=" * 70)
        logger.info(f"BTC 15-Min Trading Cycle | {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        logger.info("=" * 70)

        # Get BTC 15-min markets
        markets = self.get_btc_15min_markets()
        if not markets:
            logger.warning("No markets to trade")
            return 0

        # Enrich markets with orderbook data from WebSocket
        if self.ws_client:
            for market in markets:
                orderbook = self.ws_client.get_orderbook(market.id)
                if orderbook:
                    market.orderbook = orderbook
                    logger.debug(f"Enriched {market.id} with orderbook data")

        # Show current positions
        if self.position_tracker.get_all_positions():
            self.position_tracker.print_positions()

        # Run strategies and execute trades immediately
        executed_count = 0
        for strategy in self.strategies:
            if not strategy.enabled:
                continue

            logger.info(f"Running strategy: {strategy.name}")
            try:
                # Get current positions for this strategy
                strategy_positions = self.position_tracker.get_strategy_positions(strategy.name)
                signals = strategy.analyze(markets, strategy_positions)

                # Process each signal from this strategy
                for signal in signals:
                    trade = signal.trade
                    market = signal.market

                    # For BUY trades, check if position already exists
                    if trade.action == "BUY":
                        existing_position = self.position_tracker.get_position(
                            strategy_name=strategy.name,
                            market_id=market.id,
                            side=trade.side
                        )

                        if existing_position:
                            logger.info(f"  [{strategy.name}] Already has position in {market.question[:40]}, skipping")
                            continue

                    # For SELL trades, verify we have a position to sell
                    elif trade.action == "SELL":
                        existing_position = self.position_tracker.get_position(
                            strategy_name=strategy.name,
                            market_id=market.id,
                            side=trade.side
                        )

                        if not existing_position:
                            logger.warning(f"  [{strategy.name}] No position to sell in {market.question[:40]}, skipping")
                            continue

                        # Limit sell amount to position size
                        if trade.amount > existing_position.shares:
                            logger.warning(f"  [{strategy.name}] Sell amount ({trade.amount}) exceeds position ({existing_position.shares}), adjusting")
                            trade.amount = existing_position.shares

                    # Execute trade
                    if self.dry_run:
                        logger.info(f"  [DRY RUN] Would execute trade:")
                        logger.info(f"    Market: {trade.question[:60]}")
                        logger.info(f"    Action: {trade.action} {trade.amount} {trade.side} @ ${trade.price:.3f}")

                        if trade.action == "BUY":
                            logger.info(f"    Cost: ${trade.amount * trade.price:.2f}")
                        else:  # SELL
                            logger.info(f"    Revenue: ${trade.amount * trade.price:.2f}")

                        logger.info(f"    Reason: {trade.reason}")

                        # Track position for this strategy
                        # For SELL, pass negative shares to reduce/close position
                        shares = trade.amount if trade.action == "BUY" else -trade.amount

                        self.position_tracker.add_position(
                            strategy_name=strategy.name,
                            market_id=trade.market_id,
                            question=trade.question,
                            side=trade.side,
                            shares=shares,
                            entry_price=trade.price,
                            market_close_time=market.end_date
                        )
                        executed_count += 1
                    else:
                        success = self.client.execute_trade(trade)
                        if success:
                            # For SELL, pass negative shares to reduce/close position
                            shares = trade.amount if trade.action == "BUY" else -trade.amount

                            self.position_tracker.add_position(
                                strategy_name=strategy.name,
                                market_id=trade.market_id,
                                question=trade.question,
                                side=trade.side,
                                shares=shares,
                                entry_price=trade.price,
                                market_close_time=market.end_date
                            )
                            executed_count += 1
                            logger.info(f"  [SUCCESS] Trade executed")

            except Exception as e:
                logger.error(f"Strategy {strategy.name} failed: {e}", exc_info=True)

        logger.info("=" * 70)
        logger.info(f"Cycle complete | Executed {executed_count} trades")
        logger.info(f"Total exposure: ${self.position_tracker.get_total_exposure():.2f}")
        logger.info("=" * 70)

        return executed_count

    def run(self):
        """Run the bot continuously"""
        logger.info("Starting BTC 15-Min Trading Bot...")

        # Start WebSocket client for real-time updates (Option 1)
        if self.ws_client:
            logger.info("Attempting WebSocket connection (Option 1: Public WebSocket)...")
            logger.info(f"Will fallback to REST API (Option 3) if no data received within {self.websocket_timeout}s")

            try:
                self.ws_client.connect()
                time.sleep(2)  # Give WebSocket time to establish connection

                # Get a test market to subscribe and verify WebSocket is working
                logger.info("Testing WebSocket with initial market subscription...")
                test_markets = self.get_btc_15min_markets()
                if test_markets:
                    for market in test_markets:
                        self.ws_client.subscribe(market.id)

                    # Wait for WebSocket to receive data
                    logger.info(f"Waiting {self.websocket_timeout}s for WebSocket data...")
                    time.sleep(self.websocket_timeout)

                    if self.websocket_healthy:
                        logger.info("✓ WebSocket is healthy - using real-time data stream")
                    else:
                        logger.warning("✗ WebSocket timeout - no data received")
                        logger.warning("Falling back to REST API polling (Option 3)")
                        self.ws_client.stop()
                        self.ws_client = None
                        self.use_websocket = False
                else:
                    logger.warning("No markets available for WebSocket test, using REST API")
                    self.ws_client.stop()
                    self.ws_client = None
                    self.use_websocket = False

            except Exception as e:
                logger.error(f"WebSocket connection failed: {e}")
                logger.warning("Falling back to REST API polling (Option 3)")
                if self.ws_client:
                    try:
                        self.ws_client.stop()
                    except:
                        pass
                    self.ws_client = None
                self.use_websocket = False

        # Log the final data source
        if self.use_websocket and self.websocket_healthy:
            logger.info("Data Source: WebSocket (real-time)")
        else:
            logger.info("Data Source: REST API (30-second polling)")

        try:
            while True:
                try:
                    self.run_once()
                except Exception as e:
                    logger.error(f"Error in trading cycle: {e}", exc_info=True)

                logger.info(f"Waiting {self.check_interval} seconds until next check...")
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("Shutting down gracefully...")
        finally:
            # Stop WebSocket client
            if self.ws_client:
                logger.info("Stopping WebSocket client...")
                self.ws_client.stop()

            logger.info("Bot stopped")
            self.position_tracker.print_positions()


def setup_logging():
    """Configure logging for the application"""
    import io
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Console handler with UTF-8 encoding
    console_handler = logging.StreamHandler(
        io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    )
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler
    if Config.LOG_FILE:
        file_handler = logging.FileHandler('btc_15min_bot.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def main():
    """Main entry point"""
    logger = setup_logging()

    logger.info("=" * 70)
    logger.info("Bitcoin 15-Minute Trading Bot Starting...")
    logger.info("=" * 70)

    # Initialize Polymarket client
    client = PolymarketClient(
        api_key=Config.POLYMARKET_API_KEY,
        private_key=Config.POLYMARKET_PRIVATE_KEY
    )

    # Initialize strategies (with more sensitive thresholds + new strategies)
    strategies = [
        # Original strategies with lower thresholds
        PriceArbitrageStrategy(shares_per_trade=10, deviation_threshold=0.01),
        MeanReversionStrategy(shares_per_trade=10, extreme_threshold=0.55),
        SimpleBalancedStrategy(shares_per_trade=10, min_edge=0.02),
        # New aggressive strategies
        MomentumStrategy(shares_per_trade=10, momentum_threshold=0.03),
        VolumeSpikeStrategy(shares_per_trade=10, volume_threshold=2000.0, min_imbalance=0.03),
        TimeBasedStrategy(shares_per_trade=15, minutes_before_close=5.0, min_edge=0.01)
    ]

    # Initialize bot
    bot = BTC15MinBot(
        client=client,
        strategies=strategies,
        check_interval=5,  # Check every 30 seconds
        dry_run=Config.DRY_RUN,
        max_markets=4  # Track next 4 markets
    )

    # Run the bot
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
