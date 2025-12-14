# Bitcoin 15-Minute Trading Bot

A specialized trading bot for Polymarket's Bitcoin UP/DOWN 15-minute markets.

## Overview

This bot focuses exclusively on BTC 15-minute binary prediction markets where traders bet on whether Bitcoin's price will go UP or DOWN in the next 15 minutes.

### Key Features

- **Position Tracking**: Maintains open positions across multiple markets
- **Multiple Strategies**: Runs several strategies simultaneously
- **Active Trading**: Can both buy and sell shares
- **Risk Management**: Focuses on the next 4 closest markets to limit exposure
- **Fast Execution**: Checks markets every 30 seconds

## Strategies

### 1. Price Arbitrage Strategy
Exploits price imbalances where UP + DOWN prices don't sum to $1.00.

**Parameters:**
- `shares_per_trade`: Number of shares to trade (default: 10)
- `deviation_threshold`: Minimum price deviation to trigger (default: $0.02)

**Logic:** If UP + DOWN < $1.00, buy the cheaper side expecting prices to normalize.

### 2. Mean Reversion Strategy
Fades extreme prices expecting them to revert to the mean (50/50).

**Parameters:**
- `shares_per_trade`: Number of shares to trade (default: 10)
- `extreme_threshold`: Price above which we fade (default: 0.60)

**Logic:** If UP > 0.60, buy DOWN. If DOWN > 0.60, buy UP.

### 3. Simple Balanced Strategy
Contrarian strategy that buys the underdog.

**Parameters:**
- `shares_per_trade`: Number of shares to trade (default: 10)
- `min_edge`: Minimum price difference to trade (default: $0.05)

**Logic:** Always buy the cheaper side if there's at least a 5 cent edge.

## Running the Bot

```bash
# Make sure you're in the project directory
cd polymarket-trading

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Run the BTC 15-min bot
python btc_15min_bot.py
```

## Configuration

The bot uses the same `.env` file as the main trading bot:

```bash
# Set to 'false' for live trading (USE WITH CAUTION!)
DRY_RUN=true

# API Credentials (required for live trading)
POLYMARKET_API_KEY=your_api_key_here
POLYMARKET_PRIVATE_KEY=your_private_key_here
```

## Bot Behavior

1. **Market Selection**: Fetches all active markets and filters for BTC 15-minute markets
2. **Focus on Next 4**: Tracks only the next 4 markets closing soonest
3. **Strategy Execution**: Runs all enabled strategies on these markets
4. **Position Tracking**: Tracks all open positions in `positions.json`
5. **Frequent Updates**: Checks every 30 seconds for new opportunities

## Position Management

Positions are tracked in `positions.json`:
- **market_id**: Unique identifier for the market
- **side**: "YES" (UP) or "NO" (DOWN)
- **shares**: Number of shares owned
- **entry_price**: Average entry price
- **entry_time**: When position was opened
- **market_close_time**: When market expires

## Risk Warning

⚠️ **This bot is experimental**

- 15-minute markets are extremely volatile
- High frequency trading can lead to significant losses
- Always start with DRY_RUN=true
- Understand each strategy before using real money
- Monitor positions closely near market expiry

## Files

- `btc_15min_bot.py` - Main bot entry point
- `strategies/btc_15min_strategies.py` - BTC-specific strategies
- `position_tracker.py` - Position tracking system
- `positions.json` - Open positions (auto-generated)
- `btc_15min_bot.log` - Bot logs

## Limitations

- Currently only detects BTC markets by searching for "BTC" or "BITCOIN" in market questions
- May not find markets if Polymarket's API doesn't return them
- Selling positions is not yet implemented (only buying)
- No integration with real-time BTC price data (yet)

## Future Enhancements

- [ ] Integrate real-time BTC price feeds for momentum strategies
- [ ] Implement position closing/selling logic
- [ ] Add technical indicators (RSI, moving averages, etc.)
- [ ] Market making strategy (provide liquidity on both sides)
- [ ] Risk limits (max exposure, max positions, etc.)
- [ ] Performance tracking and analytics
