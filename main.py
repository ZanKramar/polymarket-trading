#!/usr/bin/env python3
"""
Polymarket Trading Bot
Main entry point for the trading bot
"""

import logging
import sys
from dotenv import load_dotenv

# Load .env BEFORE importing Config
load_dotenv()

from config import Config
from polymarket_client import PolymarketClient
from trading_bot import TradingBot
from strategies.high_confidence_close_strategy import HighConfidenceCloseStrategy


def setup_logging():
    """Configure logging for the application"""
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))

    # Console handler with UTF-8 encoding
    import io
    console_handler = logging.StreamHandler(
        io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    )
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler with UTF-8 encoding
    if Config.LOG_FILE:
        file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def main():
    """Main entry point"""
    # Load environment variables
    load_dotenv()

    # Setup logging
    logger = setup_logging()

    logger.info("=" * 60)
    logger.info("Polymarket Trading Bot Starting...")
    logger.info("=" * 60)

    # Print and validate configuration
    Config.print_config()
    warnings = Config.validate()
    if warnings:
        logger.warning("Configuration warnings:")
        for warning in warnings:
            logger.warning(f"  - {warning}")
        print()

    # Initialize Polymarket client
    client = PolymarketClient(
        api_key=Config.POLYMARKET_API_KEY,
        private_key=Config.POLYMARKET_PRIVATE_KEY
    )

    # Initialize strategies
    strategies = []

    # High Confidence Close Strategy
    if Config.HCC_ENABLED:
        hcc_strategy = HighConfidenceCloseStrategy(
            hours_until_close=Config.HCC_HOURS_UNTIL_CLOSE,
            confidence_threshold=Config.HCC_CONFIDENCE_THRESHOLD,
            shares_to_buy=Config.HCC_SHARES_TO_BUY,
            min_volume=Config.HCC_MIN_VOLUME
        )
        strategies.append(hcc_strategy)

    if not strategies:
        logger.error("No strategies enabled! Please enable at least one strategy.")
        sys.exit(1)

    # Initialize trading bot
    bot = TradingBot(
        client=client,
        strategies=strategies,
        check_interval=Config.CHECK_INTERVAL,
        dry_run=Config.DRY_RUN
    )

    # Run the bot
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Print final statistics
        stats = bot.get_stats()
        logger.info("=" * 60)
        logger.info("Bot Statistics:")
        logger.info(f"  Total trades executed: {stats['total_trades_executed']}")
        logger.info(f"  Active strategies: {stats['active_strategies']}/{stats['total_strategies']}")
        logger.info(f"  Mode: {'DRY RUN' if stats['dry_run'] else 'LIVE TRADING'}")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()
