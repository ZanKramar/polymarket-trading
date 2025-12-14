import logging
import time
from typing import List, Set
from datetime import datetime
from strategies.base_strategy import BaseStrategy, TradeSignal
from polymarket_client import PolymarketClient
from paper_trader import PaperTradingTracker

logger = logging.getLogger(__name__)


class TradingBot:
    """Main trading bot that orchestrates strategies and executes trades"""

    def __init__(
        self,
        client: PolymarketClient,
        strategies: List[BaseStrategy],
        check_interval: int = 60,
        dry_run: bool = True
    ):
        """
        Initialize trading bot

        Args:
            client: Polymarket client for fetching data and executing trades
            strategies: List of strategies to run
            check_interval: Seconds between market checks
            dry_run: If True, don't execute actual trades
        """
        self.client = client
        self.strategies = strategies
        self.check_interval = check_interval
        self.dry_run = dry_run
        self.executed_trades: Set[str] = set()  # Track executed trades to avoid duplicates
        self.paper_trader = PaperTradingTracker() if dry_run else None

        logger.info(f"Initialized TradingBot with {len(strategies)} strategies")
        logger.info(f"Check interval: {check_interval} seconds")
        logger.info(f"Dry run mode: {dry_run}")
        if self.paper_trader:
            logger.info("Paper trading tracker enabled")

    def add_strategy(self, strategy: BaseStrategy):
        """Add a new strategy to the bot"""
        self.strategies.append(strategy)
        logger.info(f"Added strategy: {strategy}")

    def remove_strategy(self, strategy_name: str):
        """Remove a strategy by name"""
        self.strategies = [s for s in self.strategies if s.name != strategy_name]
        logger.info(f"Removed strategy: {strategy_name}")

    def run_once(self) -> int:
        """
        Run one iteration of the trading bot

        Returns:
            Number of trades executed
        """
        logger.info("=" * 60)
        logger.info(f"Running trading cycle at {datetime.utcnow().isoformat()}")

        # Fetch current markets (fetch up to 2000 markets using pagination)
        markets = self.client.get_markets(active_only=True, limit=100, max_markets=2000)
        if not markets:
            logger.warning("No markets fetched, skipping this cycle")
            return 0

        logger.info(f"Analyzing {len(markets)} markets")

        # Collect all trade signals from strategies
        all_signals: List[TradeSignal] = []
        for strategy in self.strategies:
            if not strategy.enabled:
                logger.debug(f"Skipping disabled strategy: {strategy.name}")
                continue

            logger.info(f"Running strategy: {strategy.name}")
            logger.info("-" * 60)
            try:
                signals = strategy.analyze(markets)
                all_signals.extend(signals)
            except Exception as e:
                logger.error(f"Strategy {strategy.name} failed: {e}", exc_info=True)

        # Execute trades
        executed_count = 0
        for signal in all_signals:
            trade = signal.trade
            market = signal.market

            # Create unique trade identifier to avoid duplicate execution
            trade_key = f"{trade.market_id}:{trade.side}:{trade.amount}"

            if trade_key in self.executed_trades:
                logger.debug(f"Skipping duplicate trade: {trade_key}")
                continue

            if self.dry_run:
                # Use paper trading tracker
                if self.paper_trader:
                    trade_id = self.paper_trader.add_trade(
                        trade=trade,
                        market_end_date=market.end_date,
                        volume=market.volume
                    )
                    logger.info(f"[OK] Paper trade recorded: {trade_id}")
                executed_count += 1
                self.executed_trades.add(trade_key)
            else:
                success = self.client.execute_trade(trade)
                if success:
                    executed_count += 1
                    self.executed_trades.add(trade_key)
                    logger.info(f"[SUCCESS] Executed trade: {trade_key}")
                else:
                    logger.error(f"[FAILED] Failed to execute trade: {trade_key}")

        logger.info("=" * 60)
        logger.info(f"Cycle complete. Executed {executed_count} trades")

        # Print paper trading stats if in dry run
        if self.dry_run and self.paper_trader and executed_count > 0:
            self.paper_trader.print_stats()

        return executed_count

    def run(self, max_iterations: int = None):
        """
        Run the trading bot continuously

        Args:
            max_iterations: Maximum number of iterations (None for infinite)
        """
        logger.info("Starting trading bot...")
        logger.info(f"Strategies: {[str(s) for s in self.strategies]}")

        iteration = 0
        try:
            while True:
                iteration += 1
                if max_iterations and iteration > max_iterations:
                    logger.info(f"Reached maximum iterations ({max_iterations})")
                    break

                try:
                    self.run_once()
                except Exception as e:
                    logger.error(f"Error in trading cycle: {e}", exc_info=True)

                # Wait before next iteration
                logger.info(f"Waiting {self.check_interval} seconds until next check...")
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("Received shutdown signal, stopping bot...")
        finally:
            logger.info("Trading bot stopped")

    def get_stats(self) -> dict:
        """Get statistics about the bot's performance"""
        return {
            'total_trades_executed': len(self.executed_trades),
            'active_strategies': len([s for s in self.strategies if s.enabled]),
            'total_strategies': len(self.strategies),
            'dry_run': self.dry_run
        }
