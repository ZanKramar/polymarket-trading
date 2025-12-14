#!/usr/bin/env python3
"""
Debug script to see actual Polymarket API response
"""

import requests
import json

print("Testing Polymarket API...")
print("=" * 60)

# Try the Gamma API
url = "https://gamma-api.polymarket.com/markets"
print(f"Fetching: {url}")

try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content Type: {response.headers.get('content-type', 'unknown')}")
    print("\nResponse structure:")
    print("-" * 60)

    data = response.json()
    print(f"Response type: {type(data)}")
    print(f"Response length: {len(data) if isinstance(data, (list, dict)) else 'N/A'}")

    if isinstance(data, list):
        print(f"\nFirst item type: {type(data[0]) if data else 'Empty list'}")
        if data:
            print("\nFirst market data:")
            print(json.dumps(data[0], indent=2))

            print("\n\nFirst market keys:")
            if isinstance(data[0], dict):
                for key in data[0].keys():
                    print(f"  - {key}: {type(data[0][key])}")
    elif isinstance(data, dict):
        print("\nResponse is a dictionary")
        print("\nKeys:")
        for key in data.keys():
            print(f"  - {key}: {type(data[key])}")
        print("\nFull response:")
        print(json.dumps(data, indent=2)[:1000])
    else:
        print(f"\nUnexpected response type: {type(data)}")
        print(data)

except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")
except json.JSONDecodeError as e:
    print(f"JSON decode error: {e}")
    print(f"Raw response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
