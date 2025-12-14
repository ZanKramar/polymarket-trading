#!/usr/bin/env python3
"""
Test script to verify your Polymarket trading bot setup
Run this to ensure everything is configured correctly
"""

import sys


def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import requests
        print("  ✓ requests")
    except ImportError:
        print("  ✗ requests - Run: pip install requests")
        return False

    try:
        from dotenv import load_dotenv
        print("  ✓ python-dotenv")
    except ImportError:
        print("  ✗ python-dotenv - Run: pip install python-dotenv")
        return False

    try:
        from config import Config
        print("  ✓ config")
    except ImportError as e:
        print(f"  ✗ config - {e}")
        return False

    try:
        from polymarket_client import PolymarketClient
        print("  ✓ polymarket_client")
    except ImportError as e:
        print(f"  ✗ polymarket_client - {e}")
        return False

    try:
        from trading_bot import TradingBot
        print("  ✓ trading_bot")
    except ImportError as e:
        print(f"  ✗ trading_bot - {e}")
        return False

    try:
        from strategies.base_strategy import BaseStrategy, Market, Trade
        print("  ✓ strategies.base_strategy")
    except ImportError as e:
        print(f"  ✗ strategies.base_strategy - {e}")
        return False

    try:
        from strategies.high_confidence_close_strategy import HighConfidenceCloseStrategy
        print("  ✓ strategies.high_confidence_close_strategy")
    except ImportError as e:
        print(f"  ✗ strategies.high_confidence_close_strategy - {e}")
        return False

    return True


def test_configuration():
    """Test that configuration is properly set up"""
    print("\nTesting configuration...")
    try:
        from dotenv import load_dotenv
        from config import Config

        load_dotenv()

        print(f"  DRY_RUN: {Config.DRY_RUN}")
        print(f"  CHECK_INTERVAL: {Config.CHECK_INTERVAL}s")
        print(f"  HCC_ENABLED: {Config.HCC_ENABLED}")
        print(f"  API_KEY: {'Set' if Config.POLYMARKET_API_KEY else 'Not set'}")
        print(f"  PRIVATE_KEY: {'Set' if Config.POLYMARKET_PRIVATE_KEY else 'Not set'}")

        if Config.DRY_RUN:
            print("  ✓ Running in safe DRY_RUN mode")
        else:
            print("  ⚠ WARNING: DRY_RUN is disabled - real trades will be executed!")

        if not Config.POLYMARKET_PRIVATE_KEY and not Config.DRY_RUN:
            print("  ✗ ERROR: No private key set but DRY_RUN is disabled!")
            return False

        warnings = Config.validate()
        if warnings:
            print("\n  Configuration warnings:")
            for warning in warnings:
                print(f"    ⚠ {warning}")

        return True

    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return False


def test_polymarket_connection():
    """Test connection to Polymarket API"""
    print("\nTesting Polymarket connection...")
    try:
        from polymarket_client import PolymarketClient

        client = PolymarketClient()
        markets = client.get_markets(active_only=True)

        if markets:
            print(f"  ✓ Successfully fetched {len(markets)} markets")
            if len(markets) > 0:
                sample = markets[0]
                print(f"  Sample market: {sample.question[:50]}...")
                print(f"  YES price: ${sample.yes_price:.3f}")
                print(f"  NO price: ${sample.no_price:.3f}")
            return True
        else:
            print("  ⚠ No markets returned (API might be down or changed)")
            return False

    except Exception as e:
        print(f"  ✗ Connection error: {e}")
        print("  This might be normal if Polymarket API has changed")
        print("  You may need to update the API client code")
        return False


def test_strategy():
    """Test that strategy can be instantiated"""
    print("\nTesting strategy...")
    try:
        from strategies.high_confidence_close_strategy import HighConfidenceCloseStrategy
        from datetime import datetime, timedelta
        from strategies.base_strategy import Market

        strategy = HighConfidenceCloseStrategy()
        print(f"  ✓ Strategy created: {strategy.name}")

        # Create a test market
        test_market = Market(
            id="test123",
            question="Test market",
            end_date=datetime.utcnow() + timedelta(minutes=30),
            yes_price=0.90,
            no_price=0.10,
            volume=1000.0,
            active=True
        )

        trades = strategy.analyze([test_market])
        if trades:
            print(f"  ✓ Strategy generated {len(trades)} trade(s) for test market")
            print(f"    {trades[0].side} @ ${trades[0].price:.3f}")
        else:
            print("  ✓ Strategy analyzed test market (no trades generated)")

        return True

    except Exception as e:
        print(f"  ✗ Strategy error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all scripts_test"""
    print("=" * 60)
    print("Polymarket Trading Bot - Setup Test")
    print("=" * 60)

    all_passed = True

    # Test imports
    if not test_imports():
        all_passed = False
        print("\n❌ Import test failed!")
        print("Run: pip install -r requirements.txt")
    else:
        print("\n✅ All imports successful!")

    # Test configuration
    if not test_configuration():
        all_passed = False
        print("\n❌ Configuration test failed!")
    else:
        print("\n✅ Configuration valid!")

    # Test Polymarket connection
    if not test_polymarket_connection():
        all_passed = False
        print("\n❌ Polymarket connection test failed!")
        print("Note: This may not be critical if the API structure has changed")
    else:
        print("\n✅ Polymarket connection successful!")

    # Test strategy
    if not test_strategy():
        all_passed = False
        print("\n❌ Strategy test failed!")
    else:
        print("\n✅ Strategy test successful!")

    # Final result
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All scripts_test passed! Your bot is ready to run.")
        print("\nNext steps:")
        print("1. Review your configuration in .env")
        print("2. Run: python main.py")
        print("3. Monitor the output and logs")
    else:
        print("⚠️  Some scripts_test failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Copy configuration: cp .env.example .env")
        print("- Check Python version: python --version (need 3.8+)")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
