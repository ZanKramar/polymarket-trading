from abc import ABC, abstractmethod
from typing import Dict, List, Optional, TYPE_CHECKING
from dataclasses import dataclass
from datetime import datetime

if TYPE_CHECKING:
    from position_tracker import Position


@dataclass
class Market:
    """Represents a Polymarket market"""
    id: str
    question: str
    end_date: datetime
    yes_price: float
    no_price: float
    volume: float
    active: bool
    orderbook: Optional[Dict] = None  # Orderbook data from WebSocket

    def time_until_close(self) -> float:
        """Returns hours until market closes"""
        delta = self.end_date - datetime.utcnow()
        return delta.total_seconds() / 3600

    def get_spread(self, side: str = "YES") -> Optional[float]:
        """Get bid-ask spread for a side"""
        if not self.orderbook or side not in self.orderbook:
            return None

        bids = self.orderbook[side].get('bids', [])
        asks = self.orderbook[side].get('asks', [])

        if not bids or not asks:
            return None

        best_bid = float(bids[0]['price'])
        best_ask = float(asks[0]['price'])
        return best_ask - best_bid

    def get_order_depth(self, side: str = "YES", levels: int = 5) -> Optional[Dict]:
        """Get orderbook depth for top N levels"""
        if not self.orderbook or side not in self.orderbook:
            return None

        bids = self.orderbook[side].get('bids', [])[:levels]
        asks = self.orderbook[side].get('asks', [])[:levels]

        return {
            'bids': bids,
            'asks': asks,
            'bid_volume': sum(float(b.get('size', 0)) for b in bids),
            'ask_volume': sum(float(a.get('size', 0)) for a in asks)
        }


@dataclass
class Trade:
    """Represents a trade to execute"""
    market_id: str
    question: str
    side: str  # "YES" or "NO" (or "UP"/"DOWN" for BTC markets)
    amount: int
    price: float
    reason: str
    action: str = "BUY"  # "BUY" or "SELL"


@dataclass
class TradeSignal:
    """Bundles a trade with its source market for tracking"""
    trade: Trade
    market: Market


class BaseStrategy(ABC):
    """Base class for all trading strategies"""

    def __init__(self, name: str):
        self.name = name
        self.enabled = True

    @abstractmethod
    def analyze(self, markets: List[Market], positions: Optional[List] = None) -> List[TradeSignal]:
        """
        Analyze markets and return list of trade signals to execute.

        Args:
            markets: List of available markets
            positions: List of current Position objects for this strategy (for generating SELL signals)

        Returns:
            List of TradeSignal objects to execute (can include both BUY and SELL)
        """
        pass

    def enable(self):
        """Enable this strategy"""
        self.enabled = True

    def disable(self):
        """Disable this strategy"""
        self.enabled = False

    def __str__(self):
        return f"{self.name} ({'enabled' if self.enabled else 'disabled'})"
