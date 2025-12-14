"""
Paper trading tracker for simulating trades and tracking performance
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from strategies.base_strategy import Trade

logger = logging.getLogger(__name__)


@dataclass
class PaperTrade:
    """Represents a simulated paper trade"""
    trade_id: str
    market_id: str
    question: str
    side: str
    amount: int
    entry_price: float
    entry_time: str
    reason: str
    volume: float
    market_end_date: str

    # Resolution tracking
    resolved: bool = False
    resolution_outcome: Optional[str] = None  # "YES" or "NO"
    exit_price: Optional[float] = None
    profit_loss: Optional[float] = None

    def calculate_pnl(self, winning_side: str) -> float:
        """Calculate profit/loss for this trade"""
        cost = self.entry_price * self.amount

        if self.side == winning_side:
            # Winning trade: each share worth $1.00
            payout = 1.00 * self.amount
            profit = payout - cost
        else:
            # Losing trade: shares worth $0.00
            profit = -cost

        self.profit_loss = profit
        self.exit_price = 1.00 if self.side == winning_side else 0.00
        return profit


class PaperTradingTracker:
    """Tracks paper trades and calculates performance"""

    def __init__(self, filename: str = "paper_trades.json"):
        self.filename = filename
        self.trades: Dict[str, PaperTrade] = {}
        self.load_trades()

    def add_trade(self, trade: Trade, market_end_date: datetime, volume: float) -> str:
        """
        Add a new paper trade

        Returns:
            Trade ID
        """
        trade_id = f"{trade.market_id}:{trade.side}:{datetime.utcnow().isoformat()}"

        paper_trade = PaperTrade(
            trade_id=trade_id,
            market_id=trade.market_id,
            question=trade.question,
            side=trade.side,
            amount=trade.amount,
            entry_price=trade.price,
            entry_time=datetime.utcnow().isoformat(),
            reason=trade.reason,
            volume=volume,
            market_end_date=market_end_date.isoformat()
        )

        self.trades[trade_id] = paper_trade

        logger.info(f">>> Paper Trade Recorded <<<")
        logger.info(f"   Market: {trade.question[:60]}...")
        logger.info(f"   Side: {trade.side} | Amount: {trade.amount} shares @ ${trade.price:.3f}")
        logger.info(f"   Cost: ${trade.price * trade.amount:.2f}")
        logger.info(f"   Volume: ${volume:,.2f}")
        logger.info(f"   Closes: {market_end_date.strftime('%Y-%m-%d %H:%M UTC')}")
        logger.info(f"   Reason: {trade.reason}")
        logger.info(f"   Trade ID: {trade_id}")

        self.save_trades()
        return trade_id

    def resolve_trade(self, trade_id: str, winning_side: str):
        """Mark a trade as resolved with the outcome"""
        if trade_id not in self.trades:
            logger.warning(f"Trade {trade_id} not found for resolution")
            return

        trade = self.trades[trade_id]
        if trade.resolved:
            logger.debug(f"Trade {trade_id} already resolved")
            return

        trade.resolved = True
        trade.resolution_outcome = winning_side
        pnl = trade.calculate_pnl(winning_side)

        status = "[WIN]" if pnl > 0 else "[LOSS]"
        logger.info(f"{status} | {trade.question[:50]}")
        logger.info(f"   Bought {trade.amount} {trade.side} @ ${trade.entry_price:.3f}")
        logger.info(f"   Market resolved: {winning_side}")
        logger.info(f"   P/L: ${pnl:+.2f}")

        self.save_trades()

    def get_stats(self) -> dict:
        """Calculate and return performance statistics"""
        total_trades = len(self.trades)
        resolved_trades = [t for t in self.trades.values() if t.resolved]
        pending_trades = [t for t in self.trades.values() if not t.resolved]

        winning_trades = [t for t in resolved_trades if t.profit_loss and t.profit_loss > 0]
        losing_trades = [t for t in resolved_trades if t.profit_loss and t.profit_loss <= 0]

        total_profit = sum(t.profit_loss for t in resolved_trades if t.profit_loss)
        total_invested = sum(t.entry_price * t.amount for t in self.trades.values())

        win_rate = (len(winning_trades) / len(resolved_trades) * 100) if resolved_trades else 0

        return {
            'total_trades': total_trades,
            'resolved_trades': len(resolved_trades),
            'pending_trades': len(pending_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_profit': total_profit,
            'total_invested': total_invested,
            'roi': (total_profit / total_invested * 100) if total_invested > 0 else 0
        }

    def print_stats(self):
        """Print formatted statistics"""
        stats = self.get_stats()

        logger.info("=" * 60)
        logger.info("PAPER TRADING PERFORMANCE")
        logger.info("=" * 60)
        logger.info(f"Total Trades: {stats['total_trades']}")
        logger.info(f"  - Resolved: {stats['resolved_trades']}")
        logger.info(f"  - Pending: {stats['pending_trades']}")
        logger.info("")
        logger.info(f"Win Rate: {stats['win_rate']:.1f}%")
        logger.info(f"  - Wins: {stats['winning_trades']}")
        logger.info(f"  - Losses: {stats['losing_trades']}")
        logger.info("")
        logger.info(f"Total Invested: ${stats['total_invested']:.2f}")
        logger.info(f"Total Profit/Loss: ${stats['total_profit']:+.2f}")
        logger.info(f"ROI: {stats['roi']:+.1f}%")
        logger.info("=" * 60)

    def get_pending_trades(self) -> List[PaperTrade]:
        """Get all unresolved trades"""
        return [t for t in self.trades.values() if not t.resolved]

    def save_trades(self):
        """Save trades to JSON file"""
        try:
            data = {
                trade_id: asdict(trade)
                for trade_id, trade in self.trades.items()
            }
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save paper trades: {e}")

    def load_trades(self):
        """Load trades from JSON file"""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.trades = {
                    trade_id: PaperTrade(**trade_data)
                    for trade_id, trade_data in data.items()
                }
            logger.info(f"Loaded {len(self.trades)} paper trades from {self.filename}")
        except FileNotFoundError:
            logger.info(f"No existing paper trades file found, starting fresh")
            self.trades = {}
        except Exception as e:
            logger.error(f"Failed to load paper trades: {e}")
            self.trades = {}
