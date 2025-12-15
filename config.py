import os
from typing import Optional


class Config:
    """Configuration for the Polymarket trading bot"""

    # Polymarket API credentials
    POLYMARKET_API_KEY: Optional[str] = os.getenv("POLYMARKET_API_KEY")
    POLYMARKET_PRIVATE_KEY: Optional[str] = os.getenv("POLYMARKET_PRIVATE_KEY")

    # Bot settings
    DRY_RUN: bool = os.getenv("DRY_RUN", "true").lower() == "true"
    CHECK_INTERVAL: int = int(os.getenv("CHECK_INTERVAL", "60"))  # seconds

    # Strategy: High Confidence Close
    HCC_ENABLED: bool = os.getenv("HCC_ENABLED", "true").lower() == "true"
    HCC_HOURS_UNTIL_CLOSE: float = float(os.getenv("HCC_HOURS_UNTIL_CLOSE", "720.0"))  # 30 days default
    HCC_CONFIDENCE_THRESHOLD: float = float(os.getenv("HCC_CONFIDENCE_THRESHOLD", "0.85"))
    HCC_SHARES_TO_BUY: int = int(os.getenv("HCC_SHARES_TO_BUY", "1"))
    HCC_MIN_VOLUME: float = float(os.getenv("HCC_MIN_VOLUME", "100"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", "trading_bot.log")

    @classmethod
    def validate(cls):
        """Validate configuration"""
        warnings = []

        if cls.DRY_RUN:
            warnings.append("Running in DRY RUN mode - no real trades will be executed")

        if not cls.POLYMARKET_PRIVATE_KEY and not cls.DRY_RUN:
            warnings.append("No POLYMARKET_PRIVATE_KEY set - trades cannot be executed!")

        if cls.CHECK_INTERVAL < 10:
            warnings.append("CHECK_INTERVAL is very low - may cause rate limiting")

        return warnings

    @classmethod
    def print_config(cls):
        """Print current configuration (hiding sensitive data)"""
        print("=" * 60)
        print("Configuration:")
        print(f"  DRY_RUN: {cls.DRY_RUN}")
        print(f"  CHECK_INTERVAL: {cls.CHECK_INTERVAL} seconds")
        print(f"  API_KEY: {'Set' if cls.POLYMARKET_API_KEY else 'Not set'}")
        print(f"  PRIVATE_KEY: {'Set' if cls.POLYMARKET_PRIVATE_KEY else 'Not set'}")
        print(f"  LOG_LEVEL: {cls.LOG_LEVEL}")
        print()
        print("Strategy: High Confidence Close")
        print(f"  Enabled: {cls.HCC_ENABLED}")
        print(f"  Hours until close: {cls.HCC_HOURS_UNTIL_CLOSE}")
        print(f"  Confidence threshold: {cls.HCC_CONFIDENCE_THRESHOLD}")
        print(f"  Shares to buy: {cls.HCC_SHARES_TO_BUY}")
        print(f"  Minimum volume: {cls.HCC_MIN_VOLUME}")
        print("=" * 60)
