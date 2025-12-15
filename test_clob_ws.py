"""
Test WebSocket using py-clob-client's approach
Check Polymarket docs for correct WebSocket implementation
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("Polymarket CLOB WebSocket Research")
print("=" * 70)

# According to Polymarket docs, WebSocket subscriptions work differently
# Let's check if unauthenticated subscription works first

import websocket
import json
import time
import threading

messages = []
connected = False


def on_message(ws, message):
    print(f"\n[MESSAGE]: {message[:300]}")
    messages.append(message)


def on_error(ws, error):
    print(f"\n[ERROR]: {error}")


def on_close(ws, code, msg):
    print(f"\n[CLOSED]: Code={code}, Msg={msg}")


def on_open(ws):
    global connected
    connected = True
    print("\n[CONNECTED]")

    # Try unauthenticated subscription first
    # According to docs, some market data might be public
    subscription = {
        "type": "subscribe",
        "channel": "market",
        "market": "21742633143462"  # Try a different active market
    }

    print(f"[SUBSCRIBING - NO AUTH]: {json.dumps(subscription)}")
    ws.send(json.dumps(subscription))


# Test 1: Unauthenticated subscription
print("\nTEST 1: Unauthenticated Subscription")
print("Trying to subscribe without authentication...")

ws = websocket.WebSocketApp(
    "wss://ws-subscriptions-clob.polymarket.com/ws/market",
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
    on_open=on_open
)

wst = threading.Thread(target=ws.run_forever)
wst.daemon = True
wst.start()

time.sleep(10)
ws.close()
time.sleep(1)

print(f"\n[RESULT]: Connected={connected}, Messages={len(messages)}")

if len(messages) > 0:
    print("\nSUCCESS: Unauthenticated subscriptions work!")
    print("The issue is with the authentication format/credentials")
else:
    print("\nFAIL: Even unauthenticated subscriptions don't work")
    print("The WebSocket endpoint might require authentication for all subscriptions")

print("\n" + "=" * 70)
print("RECOMMENDATIONS:")
print("=" * 70)
print("\n1. Verify your API credentials are generated correctly:")
print("   - Use py-clob-client to create_or_derive_api_creds()")
print("   - Ensure you're using the correct signature_type")
print("\n2. Check Polymarket WebSocket documentation:")
print("   - https://docs.polymarket.com/")
print("   - Look for WebSocket subscription examples")
print("\n3. The API key/secret/passphrase might be:")
print("   - Expired or invalid")
print("   - Generated for the wrong network (testnet vs mainnet)")
print("   - Missing required permissions")
print("\n4. Try regenerating credentials using:")
print("   python -c \"from py_clob_client.client import ClobClient; ...")
print("=" * 70)
