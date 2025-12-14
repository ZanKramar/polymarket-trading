"""
Template for creating new trading strategies.
Copy this file and modify it to create your own strategy.
"""

from typing import List
import logging
from .base_strategy import BaseStrategy, Market, Trade

logger = logging.getLogger(__name__)


class TemplateStrategy(BaseStrategy):
    """
    Template strategy - replace with your strategy description

    Describe what this strategy does and when it triggers trades.
    """

    def __init__(
        self,
        name: str = "TemplateStrategy",
        # Add your custom parameters here
        param1: float = 0.5,
        param2: int = 10
    ):
        """
        Initialize the strategy

        Args:
            name: Strategy name
            param1: Description of parameter 1
            param2: Description of parameter 2
        """
        super().__init__(name)
        self.param1 = param1
        self.param2 = param2

        logger.info(f"Initialized {name} strategy:")
        logger.info(f"  - Parameter 1: {param1}")
        logger.info(f"  - Parameter 2: {param2}")

    def analyze(self, markets: List[Market]) -> List[Trade]:
        """
        Analyze markets and return list of trades to execute

        Args:
            markets: List of available markets

        Returns:
            List of Trade objects to execute
        """
        trades = []

        for market in markets:
            # Skip if market is not active
            if not market.active:
                continue

            # Add your custom logic here
            if self._should_trade_yes(market):
                trade = Trade(
                    market_id=market.id,
                    question=market.question,
                    side="YES",
                    amount=1,  # Customize this
                    price=market.yes_price,
                    reason=f"Your reason here: {market.yes_price:.3f}"
                )
                trades.append(trade)
                logger.info(f"Signal: {trade.reason} for '{market.question}'")

            elif self._should_trade_no(market):
                trade = Trade(
                    market_id=market.id,
                    question=market.question,
                    side="NO",
                    amount=1,  # Customize this
                    price=market.no_price,
                    reason=f"Your reason here: {market.no_price:.3f}"
                )
                trades.append(trade)
                logger.info(f"Signal: {trade.reason} for '{market.question}'")

        if trades:
            logger.info(f"{self.name} generated {len(trades)} trade signals")
        else:
            logger.debug(f"{self.name} found no trading opportunities")

        return trades

    def _should_trade_yes(self, market: Market) -> bool:
        """
        Determine if we should buy YES shares

        Args:
            market: Market to analyze

        Returns:
            True if we should trade YES
        """
        # Replace with your custom logic
        # Example: return market.yes_price > self.param1
        return False

    def _should_trade_no(self, market: Market) -> bool:
        """
        Determine if we should buy NO shares

        Args:
            market: Market to analyze

        Returns:
            True if we should trade NO
        """
        # Replace with your custom logic
        # Example: return market.no_price > self.param1
        return False


# Example: More sophisticated strategy
class AdvancedTemplateStrategy(BaseStrategy):
    """
    More advanced template showing additional features
    """

    def __init__(self, name: str = "AdvancedTemplate"):
        super().__init__(name)
        self.trade_history = []  # Track your own history if needed
        self.market_cache = {}   # Cache market data if needed

    def analyze(self, markets: List[Market]) -> List[Trade]:
        trades = []

        for market in markets:
            # Calculate custom metrics
            price_spread = abs(market.yes_price - market.no_price)
            time_left = market.time_until_close()

            # Apply complex logic
            score = self._calculate_market_score(market)

            if score > 0.8:  # Your threshold
                side = "YES" if market.yes_price > market.no_price else "NO"
                price = market.yes_price if side == "YES" else market.no_price

                trade = Trade(
                    market_id=market.id,
                    question=market.question,
                    side=side,
                    amount=self._calculate_position_size(market, score),
                    price=price,
                    reason=f"Score: {score:.2f}, Spread: {price_spread:.3f}, Time: {time_left:.1f}h"
                )
                trades.append(trade)

        return trades

    def _calculate_market_score(self, market: Market) -> float:
        """Calculate a score for the market (0-1)"""
        # Implement your scoring logic
        score = 0.0

        # Example factors:
        # - Price confidence
        # - Volume
        # - Time until close
        # - Historical performance
        # - External data sources

        return score

    def _calculate_position_size(self, market: Market, score: float) -> int:
        """Calculate how many shares to buy based on confidence"""
        # Example: scale position size with confidence
        base_size = 1
        multiplier = min(int(score * 5), 10)  # Max 10x
        return base_size * multiplier
