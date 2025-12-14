"""
Test script to debug BTC 15-min market API calls
"""

import requests
from datetime import datetime, timedelta

# Test 1: Fetch markets closing in the next 2 hours
now = datetime.utcnow()
end_date_min = now.isoformat() + 'Z'
end_date_max = (now + timedelta(hours=2)).isoformat() + 'Z'

print("=" * 70)
print("TEST 1: Fetching markets closing in next 2 hours")
print(f"  end_date_min: {end_date_min}")
print(f"  end_date_max: {end_date_max}")
print("=" * 70)

url = "https://gamma-api.polymarket.com/markets"
params = {
    'limit': 100,
    'closed': 'false',
    'end_date_min': end_date_min,
    'end_date_max': end_date_max
}

response = requests.get(url, params=params, timeout=10)
markets = response.json()

print(f"Found {len(markets)} markets")
for i, market in enumerate(markets[:10], 1):  # Show first 10
    question = market.get('question', 'N/A')
    slug = market.get('slug', 'N/A')
    end_date = market.get('endDate', 'N/A')
    print(f"\n{i}. {question[:70]}")
    print(f"   Slug: {slug[:70]}")
    print(f"   Ends: {end_date}")

# Test 2: Search for BTC-specific markets
print("\n" + "=" * 70)
print("TEST 2: Searching all markets for BTC/Bitcoin keywords")
print("=" * 70)

params2 = {
    'limit': 100,
    'closed': 'false'
}

response2 = requests.get(url, params=params2, timeout=10)
all_markets = response2.json()

btc_markets = []
for market in all_markets:
    question = market.get('question', '')
    slug = market.get('slug', '')
    if ('btc' in question.lower() or 'bitcoin' in question.lower() or
        'btc' in slug.lower()):
        btc_markets.append(market)

print(f"Found {len(btc_markets)} BTC-related markets out of {len(all_markets)} total")
for i, market in enumerate(btc_markets[:10], 1):
    question = market.get('question', 'N/A')
    slug = market.get('slug', 'N/A')
    end_date = market.get('endDate', 'N/A')
    print(f"\n{i}. {question[:70]}")
    print(f"   Slug: {slug[:70]}")
    print(f"   Ends: {end_date}")
