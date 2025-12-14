"""
Example: Simple arbitrage strategy
This is a demonstration strategy showing how to implement different trading logic.

This strategy looks for markets where YES + NO prices don't sum to ~$1.00,
which could indicate a pricing inefficiency.

NOTE: This is for educational purposes. Real arbitrage on Polymarket is complex
due to fees, slippage, and the need to hold positions until resolution.
"""

from typing import List
import logging
from .base_strategy import BaseStrategy, Market, Trade

logger = logging.getLogger(__name__)


class SimpleArbitrageStrategy(BaseStrategy):
    """
    Looks for pricing inefficiencies where YES + NO prices deviate from 1.0

    In an efficient market, YES + NO should always equal ~$1.00
    Deviations might indicate opportunities (though fees and slippage apply)
    """

    def __init__(
        self,
        name: str = "SimpleArbitrage",
        min_deviation: float = 0.05,  # 5 cents deviation minimum
        min_volume: float = 1000.0,   # Only trade liquid markets
        shares_to_buy: int = 1
    ):
        """
        Initialize the arbitrage strategy

        Args:
            name: Strategy name
            min_deviation: Minimum price deviation to trade (in dollars)
            min_volume: Minimum market volume to consider
            shares_to_buy: Number of shares per trade
        """
        super().__init__(name)
        self.min_deviation = min_deviation
        self.min_volume = min_volume
        self.shares_to_buy = shares_to_buy

        logger.info(f"Initialized {name} strategy:")
        logger.info(f"  - Min deviation: ${min_deviation:.2f}")
        logger.info(f"  - Min volume: ${min_volume:.2f}")
        logger.info(f"  - Shares per trade: {shares_to_buy}")

    def analyze(self, markets: List[Market]) -> List[Trade]:
        """
        Find markets with pricing inefficiencies

        Args:
            markets: List of available markets

        Returns:
            List of trades to execute
        """
        trades = []

        for market in markets:
            if not market.active:
                continue

            if market.volume < self.min_volume:
                continue

            # Calculate the sum of YES and NO prices
            price_sum = market.yes_price + market.no_price
            deviation = abs(1.0 - price_sum)

            # If prices sum to less than $1.00, there might be an opportunity
            # to buy both sides (though this requires more sophisticated execution)
            if price_sum < (1.0 - self.min_deviation):
                # Prices sum to less than they should
                # In theory, you could buy both YES and NO
                logger.info(
                    f"Underpriced market found: '{market.question}' "
                    f"(YES: ${market.yes_price:.3f} + NO: ${market.no_price:.3f} "
                    f"= ${price_sum:.3f}, deviation: ${deviation:.3f})"
                )

                # This is where you'd implement actual arbitrage logic
                # For demonstration, we'll buy the cheaper side
                if market.yes_price < market.no_price:
                    trade = Trade(
                        market_id=market.id,
                        question=market.question,
                        side="YES",
                        amount=self.shares_to_buy,
                        price=market.yes_price,
                        reason=f"Arbitrage opportunity: total price ${price_sum:.3f} < $1.00"
                    )
                    trades.append(trade)

            # If prices sum to more than $1.00, they're overpriced
            # In theory you could short (sell shares you don't own)
            # but this requires more complex implementation
            elif price_sum > (1.0 + self.min_deviation):
                logger.info(
                    f"Overpriced market found: '{market.question}' "
                    f"(YES: ${market.yes_price:.3f} + NO: ${market.no_price:.3f} "
                    f"= ${price_sum:.3f}, deviation: ${deviation:.3f})"
                )
                # Would require selling shares we don't own (shorting)
                # Not implemented in this simple example

        if trades:
            logger.info(f"{self.name} generated {len(trades)} trade signals")
        else:
            logger.debug(f"{self.name} found no arbitrage opportunities")

        return trades


# To enable this strategy, add to main.py:
#
# from strategies.example_arbitrage_strategy import SimpleArbitrageStrategy
#
# # In main() function:
# arbitrage_strategy = SimpleArbitrageStrategy(
#     min_deviation=0.05,
#     min_volume=1000.0,
#     shares_to_buy=1
# )
# strategies.append(arbitrage_strategy)
