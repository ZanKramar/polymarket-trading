# Polymarket Trading Bots

Automated trading bots for Polymarket with modular strategy architecture. Includes a general-purpose bot and a specialized Bitcoin 15-minute market bot.

## Quick Links

- **New to Polymarket?** Read [Getting Started](docs/POLYMARKET.md) - Account setup, API keys, and Polymarket basics
- **Quick Setup?** See [Quick Start Guide](docs/QUICKSTART.md) - Get running in 5 minutes
- **BTC 15-Min Bot?** See [BTC Bot Documentation](docs/BTC_15MIN_README.md) - Specialized Bitcoin trading

## Repository Structure

```
polymarket-trading/
├── docs/                          # Documentation
│   ├── POLYMARKET.md             # Polymarket basics
│   ├── QUICKSTART.md             # Setup guide
│   ├── BTC_15MIN_README.md       # BTC bot documentation
│   └── PROJECT_OVERVIEW.md       # Project overview
├── strategies/                    # Trading strategies
│   ├── base_strategy.py          # Base classes (Market, Trade, BaseStrategy)
│   ├── high_confidence_close_strategy.py  # General market strategy
│   └── btc_15min_strategies.py   # BTC 15-min strategies
├── tests/                         # Test and debug scripts
│   ├── test_*.py                 # API tests
│   ├── check_*.py                # Investigation scripts
│   └── debug_api.py              # Debug utilities
├── main.py                        # General trading bot
├── btc_15min_bot.py              # BTC 15-minute specialized bot
├── trading_bot.py                # Main bot orchestrator
├── polymarket_client.py          # Polymarket API client
├── websocket_client.py           # Real-time WebSocket updates
├── position_tracker.py           # Position management
├── paper_trader.py               # Paper trading tracker
├── config.py                      # Configuration management
├── .env.example                   # Environment variables template
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Features

### General Features
- **Modular Strategy System**: Easily add, remove, or modify trading strategies
- **Independent Trade Execution**: Each strategy operates independently
- **Dry Run Mode**: Test strategies without risking real money
- **Comprehensive Logging**: Track all decisions and trades
- **Paper Trading**: Simulated trading with performance tracking
- **Position Tracking**: Monitor open positions and P/L
- **Real-time WebSocket Updates**: Live price monitoring (CLOB API)

### BTC 15-Minute Bot Features
- **Specialized Market Discovery**: Finds restricted BTC 15-min markets using slug generation
- **6 Advanced Strategies**: Price arbitrage, mean reversion, momentum, volume spike, time-based, and balanced trading
- **Real-time Price Monitoring**: WebSocket integration for instant updates
- **Position Management**: Tracks multiple simultaneous positions
- **30-Second Cycle**: Fast response to market changes

## Available Bots

### 1. General Trading Bot (`main.py`)

General-purpose bot for all Polymarket markets.

**Strategy: High Confidence Close**
- Trades markets closing within 1 hour
- Requires 85%+ confidence (price ≥ $0.85)
- Configurable via `.env`

**Run:**
```bash
python main.py
```

### 2. BTC 15-Minute Bot (`btc_15min_bot.py`)

Specialized bot for Bitcoin UP/DOWN 15-minute markets.

**6 Built-in Strategies:**
1. **PriceArbitrage**: Exploits when UP + DOWN ≠ $1.00 (threshold: $0.01)
2. **MeanReversion**: Fades extreme prices >55%
3. **SimpleBalanced**: Contrarian - buys cheaper side (min edge: $0.02)
4. **Momentum**: Follows price trends (≥$0.03 movement)
5. **VolumeSpike**: Trades high-volume markets (>$2000 volume)
6. **TimeBased**: Aggressive trading in final 5 minutes

**Run:**
```bash
python btc_15min_bot.py
```

**Key Features:**
- Automatically discovers BTC 15-min markets (even restricted ones)
- Tracks next 4 markets simultaneously
- 30-second check interval
- Real-time WebSocket price updates
- Position tracking with P/L calculation

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   # Copy example config
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/Mac

   # Edit .env with your settings
   ```

3. **Basic `.env` configuration:**
   ```env
   # Start in dry run mode
   DRY_RUN=true

   # Check interval
   CHECK_INTERVAL=60

   # Strategy settings (for general bot)
   HCC_ENABLED=true
   HCC_HOURS_UNTIL_CLOSE=1.0
   HCC_CONFIDENCE_THRESHOLD=0.85
   ```

## Usage

### Dry Run Mode (Recommended First)

**General Bot:**
```bash
python main.py
```

**BTC 15-Min Bot:**
```bash
python btc_15min_bot.py
```

Both bots will:
- Monitor markets in real-time
- Log potential trades without executing
- Track paper trading performance
- Display position tracking

### Real Trading (Advanced)

⚠️ **Only after thorough testing!**

1. **Get Polymarket credentials:**
   - API key from Polymarket dashboard
   - Private key (keep secure!)

2. **Update `.env`:**
   ```env
   POLYMARKET_API_KEY=your_api_key_here
   POLYMARKET_PRIVATE_KEY=your_private_key_here
   DRY_RUN=false
   ```

3. **Install trading library:**
   ```bash
   pip install py-clob-client
   ```

4. **Run with real trades:**
   ```bash
   python btc_15min_bot.py  # or main.py
   ```

## Strategy Configuration

### General Bot Strategies

**High Confidence Close:**
- `HCC_ENABLED`: Enable/disable (`true`)
- `HCC_HOURS_UNTIL_CLOSE`: Max hours until close (`1.0`)
- `HCC_CONFIDENCE_THRESHOLD`: Min price to trade (`0.85`)
- `HCC_SHARES_TO_BUY`: Shares per trade (`1`)
- `HCC_MIN_VOLUME`: Min market volume (`0`)

### BTC Bot Strategies

Strategies are configured in `btc_15min_bot.py` (lines 234-243):

```python
strategies = [
    PriceArbitrageStrategy(shares_per_trade=10, deviation_threshold=0.01),
    MeanReversionStrategy(shares_per_trade=10, extreme_threshold=0.55),
    SimpleBalancedStrategy(shares_per_trade=10, min_edge=0.02),
    MomentumStrategy(shares_per_trade=10, momentum_threshold=0.03),
    VolumeSpikeStrategy(shares_per_trade=10, volume_threshold=2000.0),
    TimeBasedStrategy(shares_per_trade=15, minutes_before_close=5.0)
]
```

Adjust parameters to tune sensitivity and aggressiveness.

## Real-Time WebSocket Updates

The BTC bot includes WebSocket support for live price updates from Polymarket's CLOB API.

**Features:**
- Auto-connects on startup
- Subscribes to active markets
- Auto-reconnects on disconnection
- Falls back to REST API polling

**Note:** Full WebSocket functionality requires CLOB authentication (see WebSocket Authentication section below).

## Position Tracking

Both bots track open positions:
- Entry price and time
- Current P/L (unrealized)
- Market close time
- Position size

Positions saved to `positions.json` (git-ignored).

## Paper Trading

Dry run mode includes paper trading:
- Simulated trades tracked in `paper_trades.json`
- Performance metrics (win rate, total P/L)
- Statistics logged at shutdown

## Creating Custom Strategies

### For General Bot

1. **Create strategy file:**
```python
# strategies/my_strategy.py
from typing import List
from .base_strategy import BaseStrategy, Market, Trade

class MyCustomStrategy(BaseStrategy):
    def __init__(self, param1=10):
        super().__init__("MyCustom")
        self.param1 = param1

    def analyze(self, markets: List[Market]) -> List[Trade]:
        trades = []
        for market in markets:
            if self._should_trade(market):
                trades.append(Trade(
                    market_id=market.id,
                    question=market.question,
                    side="YES",
                    amount=10,
                    price=market.yes_price,
                    reason="Custom logic triggered"
                ))
        return trades

    def _should_trade(self, market: Market) -> bool:
        # Your logic here
        return market.yes_price > 0.60
```

2. **Register in `main.py`:**
```python
from strategies.my_strategy import MyCustomStrategy

strategies = [
    MyCustomStrategy(param1=15)
]
```

### For BTC Bot

Add to `strategies/btc_15min_strategies.py` and register in `btc_15min_bot.py`.

## Configuration Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `DRY_RUN` | Run without real trades | `true` |
| `CHECK_INTERVAL` | Seconds between checks | `60` |
| `POLYMARKET_API_KEY` | Your API key | - |
| `POLYMARKET_PRIVATE_KEY` | Your private key | - |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_FILE` | Log file path | `trading_bot.log` |

## WebSocket Authentication (Advanced)

The CLOB WebSocket endpoint (`wss://ws-subscriptions-clob.polymarket.com/ws/market`) requires authentication for full functionality.

**Current Status:**
- Basic connection works
- Subscription messages sent
- Connection drops without auth (expected)
- Bot gracefully falls back to REST API

**To Enable Full WebSocket:**

Research needed on:
1. CLOB API authentication mechanism
2. WebSocket subscription format
3. Message signing requirements

See `websocket_client.py` for implementation. Contributions welcome!

## Logs

- **Console**: Real-time bot activity
- **File Log**: Detailed debug info (`trading_bot.log`, `btc_15min_bot.log`)

## Safety Features

- ✅ Dry run mode
- ✅ Duplicate trade prevention
- ✅ Position tracking
- ✅ Paper trading simulation
- ✅ Comprehensive error handling
- ✅ Graceful shutdown
- ✅ Auto-reconnecting WebSocket

## Example Output (BTC Bot)

```
======================================================================
Bitcoin 15-Minute Trading Bot Starting...
======================================================================
Initialized PriceArbitrage strategy: $0.010 threshold
Initialized MeanReversion strategy: 0.55 threshold
Initialized SimpleBalanced strategy: $0.020 edge
Initialized Momentum strategy: $0.030 threshold
Initialized VolumeSpike strategy: $2000 volume
Initialized TimeBased strategy: 5.0 min before close

Starting WebSocket client for real-time price updates...

======================================================================
BTC 15-Min Trading Cycle | 2025-12-14 22:00:00 UTC
======================================================================
Found 1 BTC 15-min markets, tracking 1
  1. Closes in 14.5 min | UP: $0.52 | DOWN: $0.48
      Question: Bitcoin Up or Down - December 14, 10:00PM-10:15PM ET

Running strategy: SimpleBalanced
  [DRY RUN] Would execute trade:
    Market: Bitcoin Up or Down - December 14, 10:00PM-10:15PM ET
    Action: BUY 10 DOWN @ $0.480
    Cost: $4.80
    Reason: Contrarian: DOWN cheaper at 0.480 vs UP at 0.520

Cycle complete | Executed 1 trades
Total exposure: $4.80
======================================================================
```

## Troubleshooting

### No markets found
- Increase time window (`HCC_HOURS_UNTIL_CLOSE`)
- Check internet connection
- Verify Polymarket API status

### WebSocket keeps disconnecting
- Expected behavior without CLOB auth
- Bot automatically falls back to REST API
- No impact on functionality

### No trades in dry run
- Normal if markets don't meet criteria
- Adjust strategy parameters
- Check logs for analysis details

## Important Notes

1. ⚠️ **Start with dry run** - Always test first
2. 📊 **Monitor closely** - Watch bot behavior
3. 💰 **Start small** - Use small position sizes
4. 🔒 **Secure keys** - Never commit private keys
5. 📈 **Track performance** - Review paper trading results

## Test Scripts

Test scripts available in `tests/`:
- `test_btc_api.py` - Test BTC market fetching
- `test_clob_api.py` - Test CLOB API
- `check_active_market.py` - Verify market data
- `debug_api.py` - General API debugging

## Contributing

Contributions welcome, especially for:
- New trading strategies
- WebSocket authentication
- Performance improvements
- Documentation

## License

Educational purposes. Use at your own risk. Comply with Polymarket ToS.

## Disclaimer

**This bot is provided as-is without guarantees. Trading involves risk.**

Always:
- Test thoroughly in dry run
- Start with small amounts
- Monitor bot behavior
- Understand your strategies
- Be aware of fees and rules

Authors not responsible for financial losses.
