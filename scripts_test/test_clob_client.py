"""
Test the official py-clob-client to find BTC 15-min markets
"""

from py_clob_client.client import ClobClient

# Initialize the client (read-only, no auth needed)
client = ClobClient("https://clob.polymarket.com")

print("=" * 70)
print("TEST 1: Check client connection")
print("=" * 70)

# Test connection
ok = client.get_ok()
print(f"Connection OK: {ok}")

time = client.get_server_time()
print(f"Server time: {time}")

print("\n" + "=" * 70)
print("TEST 2: Get simplified markets")
print("=" * 70)

# Get simplified markets - this might show all active markets
try:
    markets = client.get_simplified_markets()
    print(f"Found {len(markets)} simplified markets")
    print(f"Type of markets: {type(markets)}")
    if markets:
        print(f"Type of first market: {type(markets[0])}")
        print(f"First market: {markets[0]}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("TEST 3: Search for markets with 'btc-updown-15m' pattern")
print("=" * 70)

try:
    # Look for any market with the btc-updown-15m pattern
    all_markets = client.get_simplified_markets()
    print(f"All markets: {all_markets}")

    # If they're strings, search in them
    btc_15min_markets = [m for m in all_markets if 'btc-updown-15m' in str(m).lower()]

    print(f"\nFound {len(btc_15min_markets)} BTC 15-min markets")

    for i, market in enumerate(btc_15min_markets[:10], 1):
        print(f"\n{i}. {market}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
