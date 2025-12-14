"""
Check the timestamp from the BTC market URL
"""

from datetime import datetime

# Timestamp from the slug: btc-updown-15m-1765733400
timestamp = 1765733400

# Convert to datetime
dt = datetime.utcfromtimestamp(timestamp)
now = datetime.utcnow()

print("=" * 70)
print("Timestamp Analysis")
print("=" * 70)
print(f"Timestamp: {timestamp}")
print(f"Date/Time (UTC): {dt}")
print(f"Current Time (UTC): {now}")
print(f"Difference: {now - dt}")

if dt < now:
    print(f"\nSTATUS: This market CLOSED {(now - dt).total_seconds() / 3600:.1f} hours ago")
    print("This explains why it's not showing up in API calls!")
else:
    print(f"\nSTATUS: This market closes in {(dt - now).total_seconds() / 3600:.1f} hours")
