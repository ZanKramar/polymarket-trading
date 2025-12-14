"""
Test accessing BTC markets through CLOB API using token IDs
"""

import requests
import json

# Token IDs from the BTC 15-min market page
token_ids = [
    "12113014551829992566277056942222952265602687336319946064267411656218135854994",
    "75883976773256527295620715381332374001360262788489574364323799973268965707663"
]

print("=" * 70)
print("TEST 1: Fetch market data using CLOB token IDs")
print("=" * 70)

clob_url = "https://clob.polymarket.com"

for token_id in token_ids:
    print(f"\nToken ID: {token_id[:20]}...")

    # Try to get the order book for this token
    try:
        url = f"{clob_url}/book?token_id={token_id}"
        print(f"URL: {url}")

        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Order book retrieved!")
            print(json.dumps(data, indent=2)[:500])
        else:
            print(f"Failed: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 70)
print("TEST 2: Try to get market info from CLOB")
print("=" * 70)

# Try to get markets endpoint
try:
    url = f"{clob_url}/markets"
    print(f"URL: {url}")

    response = requests.get(url, timeout=10)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Markets data retrieved!")
        print(f"Type: {type(data)}")

        if isinstance(data, list):
            print(f"Found {len(data)} markets")
            # Look for BTC markets
            for market in data[:10]:
                if isinstance(market, dict):
                    print(f"\nMarket: {market.get('id', 'N/A')}")
                    print(f"  Description: {str(market.get('description', 'N/A'))[:70]}")
    else:
        print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
print("TEST 3: Try to find active BTC markets via condition ID")
print("=" * 70)

# The condition ID from the page
condition_id = "0xf2aac76a461df3510f5a1ca07af38eb3af42e3e2d64d81f6de6375873aeb084e"

try:
    # Try Gamma API with condition ID
    url = f"https://gamma-api.polymarket.com/markets"
    params = {
        'condition_ids': condition_id,
        'closed': 'false'
    }

    print(f"URL: {url}")
    print(f"Params: {params}")

    response = requests.get(url, params=params, timeout=10)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        markets = response.json()
        print(f"Found {len(markets)} markets with this condition ID")
        for market in markets[:3]:
            print(f"\nQuestion: {market.get('question', 'N/A')[:70]}")
            print(f"Slug: {market.get('slug', 'N/A')}")
            print(f"End Date: {market.get('endDate', 'N/A')}")
    else:
        print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
