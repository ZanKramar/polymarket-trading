"""
Test accessing BTC 15-min markets through the Events API
"""

import requests
import json

print("=" * 70)
print("TEST 1: Fetch specific event by slug")
print("=" * 70)

# Try the event endpoint
slug = "btc-updown-15m-1765733400"
url = f"https://gamma-api.polymarket.com/events/{slug}"

print(f"URL: {url}")
try:
    response = requests.get(url, timeout=10)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nEvent data retrieved successfully!")
        print(json.dumps(data, indent=2)[:2000])  # First 2000 chars
    else:
        print(f"Failed: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
print("TEST 2: Search for BTC events")
print("=" * 70)

# Try events endpoint with search
url2 = "https://gamma-api.polymarket.com/events"
params = {
    'limit': 100,
    'closed': 'false'
}

try:
    response = requests.get(url2, params=params, timeout=10)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        events = response.json()
        print(f"Found {len(events)} events")

        # Filter for BTC events
        btc_events = []
        for event in events:
            title = event.get('title', '')
            slug = event.get('slug', '')
            if 'btc' in title.lower() or 'btc' in slug.lower() or 'bitcoin' in title.lower():
                btc_events.append(event)

        print(f"Found {len(btc_events)} BTC events")
        for event in btc_events[:5]:
            print(f"\n  Title: {event.get('title', 'N/A')[:70]}")
            print(f"  Slug: {event.get('slug', 'N/A')[:70]}")
            print(f"  Markets: {len(event.get('markets', []))}")

except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
print("TEST 3: Try to fetch current BTC 15-min events")
print("=" * 70)

# Look for events with btc-updown-15m pattern
try:
    response = requests.get(url2, params={'limit': 500, 'closed': 'false'}, timeout=10)

    if response.status_code == 200:
        events = response.json()
        btc_15min_events = []

        for event in events:
            slug = event.get('slug', '')
            if 'btc-updown-15m' in slug:
                btc_15min_events.append(event)

        print(f"Found {len(btc_15min_events)} BTC 15-min events")
        for event in btc_15min_events[:10]:
            print(f"\n  Title: {event.get('title', 'N/A')}")
            print(f"  Slug: {event.get('slug', 'N/A')}")
            print(f"  End Date: {event.get('endDate', 'N/A')}")
            print(f"  Markets: {len(event.get('markets', []))}")

except Exception as e:
    print(f"Error: {e}")
