from typing import List
import logging
from .base_strategy import BaseStrategy, Market, Trade, TradeSignal

logger = logging.getLogger(__name__)


class HighConfidenceCloseStrategy(BaseStrategy):
    """
    Strategy that buys shares of high-confidence outcomes in markets closing soon.

    Criteria:
    - Market closes in less than specified hours (default: 1 hour)
    - YES or NO share price is above confidence threshold (default: 0.85)
    - Buys specified amount of shares (default: 1)
    """

    def __init__(
        self,
        name: str = "HighConfidenceClose",
        hours_until_close: float = 1.0,
        confidence_threshold: float = 0.85,
        shares_to_buy: int = 1,
        min_volume: float = 0.0
    ):
        """
        Initialize the strategy

        Args:
            name: Strategy name
            hours_until_close: Maximum hours until market close
            confidence_threshold: Minimum price to consider (0.0-1.0)
            shares_to_buy: Number of shares to buy per trade
            min_volume: Minimum market volume to consider
        """
        super().__init__(name)
        self.hours_until_close = hours_until_close
        self.confidence_threshold = confidence_threshold
        self.shares_to_buy = shares_to_buy
        self.min_volume = min_volume

        logger.info(f"Initialized {name} strategy:")
        logger.info(f"  - Hours until close: {hours_until_close}")
        logger.info(f"  - Confidence threshold: {confidence_threshold}")
        logger.info(f"  - Shares per trade: {shares_to_buy}")
        logger.info(f"  - Minimum volume: {min_volume}")

    def analyze(self, markets: List[Market]) -> List[TradeSignal]:
        """
        Analyze markets and return trade signals for high-confidence outcomes closing soon

        Args:
            markets: List of available markets

        Returns:
            List of TradeSignal objects to execute
        """
        signals = []
        markets_checked = 0
        markets_in_time_window = 0

        # Track market distribution by closing time
        time_buckets = {
            '< 1h': 0,
            '1-6h': 0,
            '6-24h': 0,
            '1-7d': 0,
            '7-30d': 0,
            '> 30d': 0
        }

        for market in markets:
            markets_checked += 1

            # Skip if market is not active
            if not market.active:
                continue

            # Check if market closes soon enough
            hours_left = market.time_until_close()

            # Categorize into time buckets for statistics
            if hours_left < 0:
                pass  # Expired
            elif hours_left < 1:
                time_buckets['< 1h'] += 1
            elif hours_left < 6:
                time_buckets['1-6h'] += 1
            elif hours_left < 24:
                time_buckets['6-24h'] += 1
            elif hours_left < 168:  # 7 days
                time_buckets['1-7d'] += 1
            elif hours_left < 720:  # 30 days
                time_buckets['7-30d'] += 1
            else:
                time_buckets['> 30d'] += 1

            if hours_left > self.hours_until_close or hours_left < 0:
                continue

            markets_in_time_window += 1

            # Check volume requirement
            if market.volume < self.min_volume:
                logger.debug(f"Skipping low volume market: {market.question[:50]} (${market.volume:,.0f})")
                continue

            # Check if YES price is above threshold
            if market.yes_price >= self.confidence_threshold:
                trade = Trade(
                    market_id=market.id,
                    question=market.question,
                    side="YES",
                    amount=self.shares_to_buy,
                    price=market.yes_price,
                    reason=f"High confidence YES ({market.yes_price:.3f}) with {hours_left:.2f}h until close"
                )
                signal = TradeSignal(trade=trade, market=market)
                signals.append(signal)

                logger.info(f"*** OPPORTUNITY FOUND ***")
                logger.info(f"   Market: {market.question[:70]}")
                logger.info(f"   Side: YES @ ${market.yes_price:.3f} | NO @ ${market.no_price:.3f}")
                logger.info(f"   Volume: ${market.volume:,.2f}")
                logger.info(f"   Closes in: {hours_left:.2f} hours ({market.end_date.strftime('%Y-%m-%d %H:%M UTC')})")
                logger.info(f"   Action: BUY {self.shares_to_buy} YES shares")

            # Check if NO price is above threshold
            elif market.no_price >= self.confidence_threshold:
                trade = Trade(
                    market_id=market.id,
                    question=market.question,
                    side="NO",
                    amount=self.shares_to_buy,
                    price=market.no_price,
                    reason=f"High confidence NO ({market.no_price:.3f}) with {hours_left:.2f}h until close"
                )
                signal = TradeSignal(trade=trade, market=market)
                signals.append(signal)

                logger.info(f"*** OPPORTUNITY FOUND ***")
                logger.info(f"   Market: {market.question[:70]}")
                logger.info(f"   Side: YES @ ${market.yes_price:.3f} | NO @ ${market.no_price:.3f}")
                logger.info(f"   Volume: ${market.volume:,.2f}")
                logger.info(f"   Closes in: {hours_left:.2f} hours ({market.end_date.strftime('%Y-%m-%d %H:%M UTC')})")
                logger.info(f"   Action: BUY {self.shares_to_buy} NO shares")

        logger.info(f"--- Strategy Analysis Complete ---")
        logger.info(f"   Markets checked: {markets_checked}")
        logger.info(f"   Markets by closing time:")
        logger.info(f"      < 1 hour:     {time_buckets['< 1h']}")
        logger.info(f"      1-6 hours:    {time_buckets['1-6h']}")
        logger.info(f"      6-24 hours:   {time_buckets['6-24h']}")
        logger.info(f"      1-7 days:     {time_buckets['1-7d']}")
        logger.info(f"      7-30 days:    {time_buckets['7-30d']}")
        logger.info(f"      > 30 days:    {time_buckets['> 30d']}")
        logger.info(f"   Markets in time window (<{self.hours_until_close}h): {markets_in_time_window}")
        logger.info(f"   Opportunities found: {len(signals)}")

        return signals
