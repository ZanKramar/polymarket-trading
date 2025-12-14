"""
Position tracker for managing open positions across markets
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Represents an open position in a market"""
    strategy_name: str  # Strategy that owns this position
    market_id: str
    question: str
    side: str  # "UP" or "DOWN" (or "YES"/"NO" for other markets)
    shares: int  # Positive for long, negative for short (if we sold)
    entry_price: float
    entry_time: str
    market_close_time: str

    def current_value(self, current_price: float) -> float:
        """Calculate current value of position"""
        return self.shares * current_price

    def unrealized_pnl(self, current_price: float) -> float:
        """Calculate unrealized profit/loss"""
        cost_basis = self.shares * self.entry_price
        current_value = self.current_value(current_price)
        return current_value - cost_basis


class PositionTracker:
    """Tracks open positions across markets"""

    def __init__(self, filename: str = "positions.json"):
        self.filename = filename
        self.positions: Dict[str, Position] = {}
        self.load_positions()

    def add_position(self, strategy_name: str, market_id: str, question: str, side: str,
                     shares: int, entry_price: float, market_close_time: datetime) -> str:
        """
        Add a new position or update existing one for a specific strategy

        Returns:
            Position key
        """
        position_key = f"{strategy_name}:{market_id}:{side}"

        # If position already exists, update it
        if position_key in self.positions:
            existing = self.positions[position_key]
            total_shares = existing.shares + shares

            if total_shares == 0:
                # Position closed
                logger.info(f"Position closed: {position_key}")
                del self.positions[position_key]
                self.save_positions()
                return position_key
            else:
                # Average down/up the entry price
                total_cost = (existing.shares * existing.entry_price) + (shares * entry_price)
                existing.shares = total_shares
                existing.entry_price = total_cost / total_shares
                logger.info(f"Updated position {position_key}: {total_shares} shares @ ${existing.entry_price:.3f}")
        else:
            # New position
            position = Position(
                strategy_name=strategy_name,
                market_id=market_id,
                question=question,
                side=side,
                shares=shares,
                entry_price=entry_price,
                entry_time=datetime.utcnow().isoformat(),
                market_close_time=market_close_time.isoformat()
            )
            self.positions[position_key] = position
            logger.info(f"New position opened: {position_key}")
            logger.info(f"  {shares} {side} shares @ ${entry_price:.3f}")
            logger.info(f"  Cost: ${shares * entry_price:.2f}")

        self.save_positions()
        return position_key

    def get_position(self, strategy_name: str, market_id: str, side: str) -> Optional[Position]:
        """Get a specific position for a strategy"""
        position_key = f"{strategy_name}:{market_id}:{side}"
        return self.positions.get(position_key)

    def get_market_positions(self, market_id: str) -> List[Position]:
        """Get all positions for a specific market (across all strategies)"""
        return [p for p in self.positions.values() if p.market_id == market_id]

    def get_strategy_positions(self, strategy_name: str) -> List[Position]:
        """Get all positions for a specific strategy"""
        return [p for p in self.positions.values() if p.strategy_name == strategy_name]

    def get_all_positions(self) -> List[Position]:
        """Get all open positions"""
        return list(self.positions.values())

    def get_total_exposure(self) -> float:
        """Calculate total capital at risk"""
        return sum(abs(p.shares * p.entry_price) for p in self.positions.values())

    def print_positions(self):
        """Print all open positions grouped by strategy"""
        if not self.positions:
            logger.info("No open positions")
            return

        logger.info("=" * 60)
        logger.info("OPEN POSITIONS")
        logger.info("=" * 60)

        # Group by strategy
        by_strategy = {}
        for pos in self.positions.values():
            if pos.strategy_name not in by_strategy:
                by_strategy[pos.strategy_name] = []
            by_strategy[pos.strategy_name].append(pos)

        for strategy_name, positions in by_strategy.items():
            logger.info(f"\nStrategy: {strategy_name}")
            logger.info("-" * 60)
            for pos in positions:
                logger.info(f"  {pos.question[:45]}")
                logger.info(f"    {pos.shares} {pos.side} @ ${pos.entry_price:.3f}")
                logger.info(f"    Cost: ${pos.shares * pos.entry_price:.2f}")

        logger.info("=" * 60)
        logger.info(f"Total exposure: ${self.get_total_exposure():.2f}")
        logger.info("=" * 60)

    def save_positions(self):
        """Save positions to JSON file"""
        try:
            data = {
                key: asdict(pos)
                for key, pos in self.positions.items()
            }
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save positions: {e}")

    def load_positions(self):
        """Load positions from JSON file"""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.positions = {
                    key: Position(**pos_data)
                    for key, pos_data in data.items()
                }
            logger.info(f"Loaded {len(self.positions)} open positions from {self.filename}")
        except FileNotFoundError:
            logger.info(f"No existing positions file found, starting fresh")
            self.positions = {}
        except Exception as e:
            logger.error(f"Failed to load positions: {e}")
            self.positions = {}
