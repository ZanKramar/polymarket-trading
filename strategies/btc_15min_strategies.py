"""
Strategies specific to Bitcoin 15-minute UP/DOWN markets
"""

from typing import List, Optional, Dict
import logging
from datetime import datetime
from .base_strategy import BaseStrategy, Market, Trade, TradeSignal

logger = logging.getLogger(__name__)


class PriceArbitrageStrategy(BaseStrategy):
    """
    Exploits price imbalances between UP and DOWN.
    UP + DOWN should sum to approximately $1.00.
    If the sum is significantly different, there's an arbitrage opportunity.
    """

    def __init__(self, shares_per_trade: int = 10, deviation_threshold: float = 0.01):
        """
        Args:
            shares_per_trade: Number of shares to trade
            deviation_threshold: Minimum price deviation to trigger trade (e.g., 0.01 = 1 cent)
        """
        super().__init__("PriceArbitrage")
        self.shares_per_trade = shares_per_trade
        self.deviation_threshold = deviation_threshold

        logger.info(f"Initialized {self.name} strategy:")
        logger.info(f"  - Shares per trade: {shares_per_trade}")
        logger.info(f"  - Deviation threshold: ${deviation_threshold:.3f}")

    def analyze(self, markets: List[Market], positions: Optional[List] = None) -> List[TradeSignal]:
        """Look for price imbalances"""
        signals = []

        for market in markets:
            if not market.active:
                continue

            # In these markets, yes_price = UP price, no_price = DOWN price
            up_price = market.yes_price
            down_price = market.no_price
            total = up_price + down_price

            # Expected total is 1.00
            deviation = abs(total - 1.00)

            if deviation > self.deviation_threshold:
                # Prices don't sum to 1.00 - arbitrage opportunity
                if total < 1.00:
                    # Prices are undervalued - buy both sides
                    logger.info(f"Arbitrage opportunity: UP={up_price:.3f} + DOWN={down_price:.3f} = {total:.3f} < 1.00")
                    # For now, buy the cheaper side
                    if up_price < down_price:
                        trade = Trade(
                            market_id=market.id,
                            question=market.question,
                            side="YES",  # UP
                            amount=self.shares_per_trade,
                            price=up_price,
                            reason=f"Arbitrage: UP underpriced at {up_price:.3f} (total={total:.3f})"
                        )
                        signals.append(TradeSignal(trade=trade, market=market))
                    else:
                        trade = Trade(
                            market_id=market.id,
                            question=market.question,
                            side="NO",  # DOWN
                            amount=self.shares_per_trade,
                            price=down_price,
                            reason=f"Arbitrage: DOWN underpriced at {down_price:.3f} (total={total:.3f})"
                        )
                        signals.append(TradeSignal(trade=trade, market=market))

        logger.info(f"{self.name}: Found {len(signals)} opportunities")
        return signals


class MeanReversionStrategy(BaseStrategy):
    """
    Fades extreme prices. If UP or DOWN gets too expensive (>threshold),
    bet against it expecting mean reversion.
    """

    def __init__(self, shares_per_trade: int = 10, extreme_threshold: float = 0.55):
        """
        Args:
            shares_per_trade: Number of shares to trade
            extreme_threshold: Price above which we consider it extreme (e.g., 0.55)
        """
        super().__init__("MeanReversion")
        self.shares_per_trade = shares_per_trade
        self.extreme_threshold = extreme_threshold

        logger.info(f"Initialized {self.name} strategy:")
        logger.info(f"  - Shares per trade: {shares_per_trade}")
        logger.info(f"  - Extreme threshold: {extreme_threshold:.2f}")

    def analyze(self, markets: List[Market], positions: Optional[List] = None) -> List[TradeSignal]:
        """Fade extreme prices"""
        signals = []

        for market in markets:
            if not market.active:
                continue

            up_price = market.yes_price
            down_price = market.no_price

            # If UP is too expensive, buy DOWN
            if up_price > self.extreme_threshold:
                trade = Trade(
                    market_id=market.id,
                    question=market.question,
                    side="NO",  # DOWN
                    amount=self.shares_per_trade,
                    price=down_price,
                    reason=f"Mean reversion: UP overpriced at {up_price:.3f}, buying DOWN at {down_price:.3f}"
                )
                signals.append(TradeSignal(trade=trade, market=market))

            # If DOWN is too expensive, buy UP
            elif down_price > self.extreme_threshold:
                trade = Trade(
                    market_id=market.id,
                    question=market.question,
                    side="YES",  # UP
                    amount=self.shares_per_trade,
                    price=up_price,
                    reason=f"Mean reversion: DOWN overpriced at {down_price:.3f}, buying UP at {up_price:.3f}"
                )
                signals.append(TradeSignal(trade=trade, market=market))

        logger.info(f"{self.name}: Found {len(signals)} opportunities")
        return signals


class SimpleBalancedStrategy(BaseStrategy):
    """
    Simple strategy: Buy UP if it's cheaper than DOWN (market expects down),
    buy DOWN if it's cheaper than UP (market expects up).
    This is a contrarian strategy betting on randomness/noise.
    """

    def __init__(self, shares_per_trade: int = 10, min_edge: float = 0.02):
        """
        Args:
            shares_per_trade: Number of shares to trade
            min_edge: Minimum price difference to trigger trade (e.g., 0.02 = 2 cents edge)
        """
        super().__init__("SimpleBalanced")
        self.shares_per_trade = shares_per_trade
        self.min_edge = min_edge

        logger.info(f"Initialized {self.name} strategy:")
        logger.info(f"  - Shares per trade: {shares_per_trade}")
        logger.info(f"  - Minimum edge: ${min_edge:.3f}")

    def analyze(self, markets: List[Market], positions: Optional[List] = None) -> List[TradeSignal]:
        """Buy the underdog"""
        signals = []

        for market in markets:
            if not market.active:
                continue

            up_price = market.yes_price
            down_price = market.no_price
            price_diff = abs(up_price - down_price)

            # Only trade if there's a meaningful edge
            if price_diff < self.min_edge:
                continue

            # Buy the cheaper side (contrarian)
            if up_price < down_price:
                trade = Trade(
                    market_id=market.id,
                    question=market.question,
                    side="YES",  # UP
                    amount=self.shares_per_trade,
                    price=up_price,
                    reason=f"Contrarian: UP cheaper at {up_price:.3f} vs DOWN at {down_price:.3f}"
                )
                signals.append(TradeSignal(trade=trade, market=market))
            else:
                trade = Trade(
                    market_id=market.id,
                    question=market.question,
                    side="NO",  # DOWN
                    amount=self.shares_per_trade,
                    price=down_price,
                    reason=f"Contrarian: DOWN cheaper at {down_price:.3f} vs UP at {up_price:.3f}"
                )
                signals.append(TradeSignal(trade=trade, market=market))

        logger.info(f"{self.name}: Found {len(signals)} opportunities")
        return signals


class MomentumStrategy(BaseStrategy):
    """
    Follows price momentum. Tracks price changes and bets in the direction
    of movement if momentum is strong enough.
    """

    def __init__(self, shares_per_trade: int = 10, momentum_threshold: float = 0.03):
        """
        Args:
            shares_per_trade: Number of shares to trade
            momentum_threshold: Minimum price change to follow (e.g., 0.03 = 3 cents)
        """
        super().__init__("Momentum")
        self.shares_per_trade = shares_per_trade
        self.momentum_threshold = momentum_threshold
        self.last_prices: Dict[str, Dict[str, float]] = {}  # market_id -> {up_price, down_price}

        logger.info(f"Initialized {self.name} strategy:")
        logger.info(f"  - Shares per trade: {shares_per_trade}")
        logger.info(f"  - Momentum threshold: ${momentum_threshold:.3f}")

    def analyze(self, markets: List[Market], positions: Optional[List] = None) -> List[TradeSignal]:
        """Follow price momentum"""
        signals = []

        for market in markets:
            if not market.active:
                continue

            up_price = market.yes_price
            down_price = market.no_price

            # Check if we have historical data for this market
            if market.id in self.last_prices:
                last_up = self.last_prices[market.id]['up_price']
                last_down = self.last_prices[market.id]['down_price']

                up_change = up_price - last_up
                down_change = down_price - last_down

                # If UP price is rising significantly, buy UP (momentum)
                if up_change >= self.momentum_threshold:
                    trade = Trade(
                        market_id=market.id,
                        question=market.question,
                        side="YES",  # UP
                        amount=self.shares_per_trade,
                        price=up_price,
                        reason=f"Momentum: UP rising (+${up_change:.3f} to {up_price:.3f})"
                    )
                    signals.append(TradeSignal(trade=trade, market=market))

                # If DOWN price is rising significantly, buy DOWN (momentum)
                elif down_change >= self.momentum_threshold:
                    trade = Trade(
                        market_id=market.id,
                        question=market.question,
                        side="NO",  # DOWN
                        amount=self.shares_per_trade,
                        price=down_price,
                        reason=f"Momentum: DOWN rising (+${down_change:.3f} to {down_price:.3f})"
                    )
                    signals.append(TradeSignal(trade=trade, market=market))

            # Update price history
            self.last_prices[market.id] = {
                'up_price': up_price,
                'down_price': down_price
            }

        logger.info(f"{self.name}: Found {len(signals)} opportunities")
        return signals


class VolumeSpikeStrategy(BaseStrategy):
    """
    Detects unusual volume spikes and trades on the assumption that
    high volume indicates informed trading or strong conviction.
    """

    def __init__(self, shares_per_trade: int = 10, volume_threshold: float = 2000.0, min_imbalance: float = 0.03):
        """
        Args:
            shares_per_trade: Number of shares to trade
            volume_threshold: Minimum volume to consider (e.g., 2000)
            min_imbalance: Minimum price imbalance to trade on volume spike
        """
        super().__init__("VolumeSpike")
        self.shares_per_trade = shares_per_trade
        self.volume_threshold = volume_threshold
        self.min_imbalance = min_imbalance

        logger.info(f"Initialized {self.name} strategy:")
        logger.info(f"  - Shares per trade: {shares_per_trade}")
        logger.info(f"  - Volume threshold: ${volume_threshold:.0f}")
        logger.info(f"  - Min imbalance: ${min_imbalance:.3f}")

    def analyze(self, markets: List[Market], positions: Optional[List] = None) -> List[TradeSignal]:
        """Trade on high volume with price imbalance"""
        signals = []

        for market in markets:
            if not market.active:
                continue

            # Only trade if volume is high enough
            if market.volume < self.volume_threshold:
                continue

            up_price = market.yes_price
            down_price = market.no_price
            price_diff = abs(up_price - down_price)

            # High volume + imbalance = opportunity
            if price_diff >= self.min_imbalance:
                # Buy the cheaper side (assuming volume shows smart money interest)
                if up_price < down_price:
                    trade = Trade(
                        market_id=market.id,
                        question=market.question,
                        side="YES",  # UP
                        amount=self.shares_per_trade,
                        price=up_price,
                        reason=f"Volume spike: High vol (${market.volume:.0f}), UP cheaper at {up_price:.3f}"
                    )
                    signals.append(TradeSignal(trade=trade, market=market))
                else:
                    trade = Trade(
                        market_id=market.id,
                        question=market.question,
                        side="NO",  # DOWN
                        amount=self.shares_per_trade,
                        price=down_price,
                        reason=f"Volume spike: High vol (${market.volume:.0f}), DOWN cheaper at {down_price:.3f}"
                    )
                    signals.append(TradeSignal(trade=trade, market=market))

        logger.info(f"{self.name}: Found {len(signals)} opportunities")
        return signals


class TimeBasedStrategy(BaseStrategy):
    """
    More aggressive trading near market close. Takes positions based on
    the assumption that late-stage price movements are more informed.
    """

    def __init__(self, shares_per_trade: int = 15, minutes_before_close: float = 5.0, min_edge: float = 0.01):
        """
        Args:
            shares_per_trade: Number of shares to trade (higher for end-game)
            minutes_before_close: Start trading this many minutes before close
            min_edge: Minimum edge required for late trades
        """
        super().__init__("TimeBased")
        self.shares_per_trade = shares_per_trade
        self.minutes_before_close = minutes_before_close
        self.min_edge = min_edge

        logger.info(f"Initialized {self.name} strategy:")
        logger.info(f"  - Shares per trade: {shares_per_trade}")
        logger.info(f"  - Active {minutes_before_close} min before close")
        logger.info(f"  - Min edge: ${min_edge:.3f}")

    def analyze(self, markets: List[Market], positions: Optional[List] = None) -> List[TradeSignal]:
        """Aggressive trading near market close"""
        signals = []

        for market in markets:
            if not market.active:
                continue

            # Calculate time until close in minutes
            time_until_close = market.time_until_close() * 60  # Convert hours to minutes

            # Only trade if we're close to expiry
            if time_until_close > self.minutes_before_close:
                continue

            up_price = market.yes_price
            down_price = market.no_price
            price_diff = abs(up_price - down_price)

            # Take a position if there's any edge
            if price_diff >= self.min_edge:
                # Buy the cheaper side
                if up_price < down_price:
                    trade = Trade(
                        market_id=market.id,
                        question=market.question,
                        side="YES",  # UP
                        amount=self.shares_per_trade,
                        price=up_price,
                        reason=f"Late trade: {time_until_close:.1f}min left, UP at {up_price:.3f}"
                    )
                    signals.append(TradeSignal(trade=trade, market=market))
                else:
                    trade = Trade(
                        market_id=market.id,
                        question=market.question,
                        side="NO",  # DOWN
                        amount=self.shares_per_trade,
                        price=down_price,
                        reason=f"Late trade: {time_until_close:.1f}min left, DOWN at {down_price:.3f}"
                    )
                    signals.append(TradeSignal(trade=trade, market=market))

        logger.info(f"{self.name}: Found {len(signals)} opportunities")
        return signals


class CloseToExpiryStrategy(BaseStrategy):
    """
    Close positions near expiry to lock in profits or cut losses.
    This is more of a risk management strategy.
    """

    def __init__(self, minutes_before_close: float = 2.0, min_profit_to_close: float = 0.02):
        """
        Args:
            minutes_before_close: Close positions this many minutes before market close
            min_profit_to_close: Minimum profit per share to close early (e.g., 0.02 = 2 cents)
        """
        super().__init__("CloseToExpiry")
        self.minutes_before_close = minutes_before_close
        self.min_profit_to_close = min_profit_to_close

        logger.info(f"Initialized {self.name} strategy:")
        logger.info(f"  - Close {minutes_before_close} min before expiry")
        logger.info(f"  - Min profit to close: ${min_profit_to_close:.3f}")

    def analyze(self, markets: List[Market], positions: Optional[List] = None) -> List[TradeSignal]:
        """
        Note: This strategy needs access to current positions.
        It will be implemented in the bot itself.
        """
        # This strategy is implemented in the bot's position management
        return []
