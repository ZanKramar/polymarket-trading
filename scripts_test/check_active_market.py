"""
Investigate the currently active BTC 15-min market
"""

from datetime import datetime
import requests
import json

# Current active market timestamp
timestamp = 1765745100
slug = "btc-updown-15m-1765745100"

# Convert to datetime
dt = datetime.utcfromtimestamp(timestamp)
now = datetime.utcnow()

print("=" * 70)
print("ACTIVE MARKET ANALYSIS")
print("=" * 70)
print(f"Market slug: {slug}")
print(f"Timestamp: {timestamp}")
print(f"Close time (UTC): {dt}")
print(f"Current time (UTC): {now}")
print(f"Time until close: {(dt - now).total_seconds() / 60:.1f} minutes")

print("\n" + "=" * 70)
print("TEST 1: Try to fetch via Gamma Events API")
print("=" * 70)

try:
    url = f"https://gamma-api.polymarket.com/events/{slug}"
    response = requests.get(url, timeout=10)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("SUCCESS! Event data retrieved:")
        print(json.dumps(data, indent=2)[:2000])
    else:
        print(f"Failed: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
print("TEST 2: Search in /markets with slug filter")
print("=" * 70)

try:
    url = "https://gamma-api.polymarket.com/markets"
    params = {
        'slug': slug,
        'limit': 10
    }

    response = requests.get(url, params=params, timeout=10)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        markets = response.json()
        print(f"Found {len(markets)} markets")
        if markets:
            print(json.dumps(markets[0], indent=2)[:2000])
    else:
        print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
print("TEST 3: Search /events for all btc-updown-15m events")
print("=" * 70)

try:
    url = "https://gamma-api.polymarket.com/events"
    params = {
        'limit': 100,
        'closed': 'false'
    }

    response = requests.get(url, params=params, timeout=10)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        events = response.json()
        print(f"Total events: {len(events)}")

        # Filter for BTC 15-min events
        btc_events = [e for e in events if 'btc-updown-15m' in e.get('slug', '').lower()]

        print(f"BTC 15-min events: {len(btc_events)}")
        for event in btc_events[:5]:
            print(f"\n  Slug: {event.get('slug')}")
            print(f"  Title: {event.get('title', 'N/A')[:60]}")
            print(f"  End: {event.get('endDate')}")
            print(f"  Active: {event.get('active')}")
            print(f"  Closed: {event.get('closed')}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
print("TEST 4: Try to access event page content")
print("=" * 70)

try:
    # Try fetching the actual page to see what data it loads
    page_url = f"https://polymarket.com/event/{slug}"
    print(f"Page URL: {page_url}")

    # We can't scrape, but we can try the API endpoint the page would call
    api_url = f"https://gamma-api.polymarket.com/event-slug/{slug}"
    print(f"API URL: {api_url}")

    response = requests.get(api_url, timeout=10)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("SUCCESS! Event data via event-slug endpoint:")
        print(json.dumps(data, indent=2)[:3000])
except Exception as e:
    print(f"Error: {e}")
