# Quick Start Guide

Get your Polymarket trading bot up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure the Bot

```bash
# Copy the example configuration
cp .env.example .env
```

The default configuration is safe for testing (dry run mode). You don't need to change anything to start!

## Step 3: Run the Bot

```bash
python main.py
```

That's it! The bot will now:
- Check Polymarket markets every 60 seconds
- Look for markets closing in less than 1 hour
- Identify markets where YES or NO shares are priced above 85 cents
- Log potential trades (but not execute them since it's in dry run mode)

## What You'll See

```
============================================================
Polymarket Trading Bot Starting...
============================================================
Configuration:
  DRY_RUN: True
  CHECK_INTERVAL: 60 seconds
  ...

============================================================
Running trading cycle at 2025-12-14T10:30:00
Analyzing 150 markets
Running strategy: HighConfidenceClose
Cycle complete. Executed 0 trades
Waiting 60 seconds until next check...
```

## Customizing Your Bot

### Change How Often It Checks Markets

Edit `.env`:
```env
CHECK_INTERVAL=30  # Check every 30 seconds instead
```

### Adjust Strategy Parameters

Edit `.env`:
```env
HCC_HOURS_UNTIL_CLOSE=2.0      # Look at markets closing in 2 hours
HCC_CONFIDENCE_THRESHOLD=0.90   # Only trade when price is above 90 cents
HCC_SHARES_TO_BUY=5            # Buy 5 shares per trade
```

### View More Detailed Logs

Edit `.env`:
```env
LOG_LEVEL=DEBUG  # Show all debug information
```

## Next Steps

1. **Monitor the bot**: Let it run and watch what opportunities it finds
2. **Tune the strategy**: Adjust parameters based on what you observe
3. **Review the logs**: Check `trading_bot.log` for detailed information
4. **Create custom strategies**: See `strategies/strategy_template.py` for examples

## When You're Ready for Real Trading

**⚠️ WARNING: Only do this when you fully understand what the bot will do!**

1. Get your Polymarket API credentials
2. Update `.env`:
   ```env
   POLYMARKET_API_KEY=your_api_key
   POLYMARKET_PRIVATE_KEY=your_private_key
   DRY_RUN=false
   ```
3. Start with small amounts:
   ```env
   HCC_SHARES_TO_BUY=1  # Start with just 1 share
   ```
4. Monitor closely for the first few hours

## Common Issues

**"No markets fetched"**
- Check your internet connection
- Polymarket API might be temporarily down

**"No trading opportunities"**
- Try adjusting `HCC_HOURS_UNTIL_CLOSE` to a larger value
- Lower `HCC_CONFIDENCE_THRESHOLD` to find more opportunities
- This is normal if there aren't many markets closing soon

**Import errors**
- Run `pip install -r requirements.txt` again
- Make sure you're using Python 3.8 or higher

## Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Review example strategies in `strategies/` directory
- Check logs in `trading_bot.log`

Happy trading! Remember to always test thoroughly before enabling real trades.
