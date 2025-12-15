"""
Simple WebSocket authentication test
"""
import os
import json
import time
import hmac
import hashlib
import base64
import websocket
from dotenv import load_dotenv

load_dotenv()

# Get credentials
API_KEY = os.getenv("POLYMARKET_API_KEY")
API_SECRET = os.getenv("POLYMARKET_API_SECRET")
API_PASSPHRASE = os.getenv("POLYMARKET_API_PASSPHRASE")

print("=" * 70)
print("WebSocket Authentication Test")
print("=" * 70)
print(f"API Key: {API_KEY[:10]}..." if API_KEY else "API Key: NOT SET")
print(f"API Secret: {'SET (base64)' if API_SECRET else 'NOT SET'}")
print(f"API Passphrase: {'SET' if API_PASSPHRASE else 'NOT SET'}")
print("=" * 70)

if not all([API_KEY, API_SECRET, API_PASSPHRASE]):
    print("ERROR: Missing credentials in .env file!")
    print("Add POLYMARKET_API_KEY, POLYMARKET_API_SECRET, POLYMARKET_API_PASSPHRASE")
    exit(1)

# Connection state
messages_received = []
connection_opened = False
error_messages = []


def generate_signature(timestamp):
    """Generate HMAC-SHA256 signature"""
    try:
        secret_bytes = base64.b64decode(API_SECRET)
        signature = hmac.new(
            secret_bytes,
            timestamp.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode('utf-8')
    except Exception as e:
        print(f"ERROR generating signature: {e}")
        return ""


def on_message(ws, message):
    print(f"\n[MESSAGE RECEIVED]")
    print(message[:500])  # Print first 500 chars
    messages_received.append(message)

    try:
        data = json.loads(message)
        print(f"Type: {data.get('type', 'unknown')}")
    except:
        pass


def on_error(ws, error):
    print(f"\n[ERROR] {error}")
    error_messages.append(str(error))


def on_close(ws, close_status_code, close_msg):
    print(f"\n[CLOSED] Code: {close_status_code}, Message: {close_msg}")


def on_open(ws):
    global connection_opened
    connection_opened = True
    print("\n[CONNECTED] WebSocket opened successfully")

    # Send authenticated subscription
    timestamp = str(int(time.time()))
    signature = generate_signature(timestamp)

    subscription = {
        "type": "subscribe",
        "channel": "market",
        "market": "929488",  # Test market ID
        "auth": {
            "apiKey": API_KEY,
            "signature": signature,
            "timestamp": timestamp,
            "passphrase": API_PASSPHRASE
        }
    }

    print(f"\n[SUBSCRIBING]")
    print(f"  Timestamp: {timestamp}")
    print(f"  Signature: {signature[:20]}...")
    print(f"  Message: {json.dumps(subscription, indent=2)}")

    ws.send(json.dumps(subscription))
    print("[SENT] Subscription message sent")


# Test connection
print("\nConnecting to: wss://ws-subscriptions-clob.polymarket.com/ws/market")

ws = websocket.WebSocketApp(
    "wss://ws-subscriptions-clob.polymarket.com/ws/market",
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
    on_open=on_open
)

# Run for 15 seconds
import threading
wst = threading.Thread(target=ws.run_forever)
wst.daemon = True
wst.start()

print("Waiting for 15 seconds...")
time.sleep(15)

ws.close()
time.sleep(1)

# Results
print("\n" + "=" * 70)
print("TEST RESULTS")
print("=" * 70)
print(f"Connection opened: {'YES' if connection_opened else 'NO'}")
print(f"Messages received: {len(messages_received)}")
print(f"Errors: {len(error_messages)}")

if error_messages:
    print("\nErrors encountered:")
    for err in error_messages:
        print(f"  - {err}")

if messages_received:
    print("\nSample messages:")
    for i, msg in enumerate(messages_received[:3]):
        print(f"\n  Message {i+1}:")
        print(f"  {msg[:200]}")

print("=" * 70)

# Diagnosis
if not connection_opened:
    print("\nDIAGNOSIS: Connection failed to open")
    print("  - Check network/firewall")
    print("  - Verify WebSocket URL is correct")
elif len(messages_received) == 0:
    print("\nDIAGNOSIS: Connected but no messages received")
    print("  - Authentication might be failing")
    print("  - Check API credentials are correct")
    print("  - Verify signature generation")
elif "Connection to remote host was lost" in str(error_messages):
    print("\nDIAGNOSIS: Connection drops after subscription")
    print("  - Server is rejecting the authentication")
    print("  - Possible issues:")
    print("    1. API key/secret/passphrase mismatch")
    print("    2. Incorrect signature format")
    print("    3. Timestamp out of sync")
else:
    print("\nDIAGNOSIS: Success! Receiving messages")

print("=" * 70)
