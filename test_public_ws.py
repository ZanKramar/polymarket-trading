"""
Test public WebSocket endpoint for market data
"""
import json
import time
import websocket
import threading

messages = []
connected = False


def on_message(ws, message):
    print(f"\n[MESSAGE RECEIVED]:")
    print(message[:500])
    messages.append(message)

    try:
        data = json.loads(message)
        print(f"Type: {data.get('event_type', data.get('type', 'unknown'))}")
        if 'market' in str(data):
            print(f"Full data: {json.dumps(data, indent=2)[:1000]}")
    except:
        pass


def on_error(ws, error):
    print(f"\n[ERROR]: {error}")


def on_close(ws, code, msg):
    print(f"\n[CLOSED]: Code={code}, Msg={msg}")


def on_open(ws):
    global connected
    connected = True
    print("\n[CONNECTED] to wss://ws-live-data.polymarket.com")

    # Subscribe to market data
    # Try different subscription formats

    # Format 1: Subscribe to specific market
    subscription = {
        "type": "subscribe",
        "channel": "market",
        "market_id": "21742633143462"  # A known active market
    }

    print(f"[SUBSCRIBING]: {json.dumps(subscription)}")
    ws.send(json.dumps(subscription))


print("=" * 70)
print("Testing Public WebSocket: wss://ws-live-data.polymarket.com")
print("=" * 70)

ws = websocket.WebSocketApp(
    "wss://ws-live-data.polymarket.com",
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
    on_open=on_open
)

wst = threading.Thread(target=ws.run_forever)
wst.daemon = True
wst.start()

print("\nWaiting 15 seconds for messages...")
time.sleep(15)

ws.close()
time.sleep(1)

print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)
print(f"Connected: {connected}")
print(f"Messages received: {len(messages)}")

if len(messages) > 0:
    print("\n✓ SUCCESS! Public WebSocket works!")
    print("\nSample messages:")
    for i, msg in enumerate(messages[:5]):
        print(f"\n--- Message {i+1} ---")
        print(msg[:300])
else:
    print("\n✗ No messages received from public WebSocket")
    print("May need different subscription format or topic")

print("=" * 70)
