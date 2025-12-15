# WebSocket Authentication Guide

This document explains how to enable authenticated WebSocket connections for real-time Polymarket price updates.

## Overview

Polymarket provides real-time data streaming via WebSocket, but full access requires authentication using CLOB API credentials.

## Authentication Levels

### L1 Authentication (Private Key)
- Uses your wallet's private key
- Proves wallet ownership via EIP-712 signatures
- Non-custodial (Polymarket never holds your funds)
- **Purpose**: Create or derive API credentials

### L2 Authentication (API Credentials)
- Uses generated API key, secret, and passphrase
- Required for WebSocket subscriptions
- Generated through L1 authentication
- **Purpose**: Authenticate WebSocket and REST API requests

## WebSocket Endpoints

Polymarket has two WebSocket services:

1. **CLOB WebSocket** (`wss://ws-subscriptions-clob.polymarket.com/ws/market`)
   - Order book updates
   - Market-specific data
   - Requires L2 auth for subscriptions

2. **Real-Time Data** (`wss://ws-live-data.polymarket.com`)
   - Broader market data
   - Activity feeds
   - Comment streams
   - Crypto/equity prices

## Generating API Credentials

### Using py-clob-client

```python
from py_clob_client.client import ClobClient

# Configuration
HOST = "https://clob.polymarket.com"
CHAIN_ID = 137  # Polygon mainnet
PRIVATE_KEY = "<your-private-key>"  # From .env
FUNDER = "<your-wallet-address>"

# Initialize client
client = ClobClient(
    HOST,
    key=PRIVATE_KEY,
    chain_id=CHAIN_ID,
    signature_type=1,  # POLY_PROXY (for Magic Link) or 0 for EOA
    funder=FUNDER
)

# Generate or derive credentials
creds = client.create_or_derive_api_creds()
print(f"API Key: {creds['apiKey']}")
print(f"Secret: {creds['secret']}")
print(f"Passphrase: {creds['passphrase']}")

# Set credentials for future use
client.set_api_creds(creds)
```

### Signature Types

Choose based on your wallet type:
- **0 (EOA)**: Standard Ethereum wallets (MetaMask, Ledger, etc.)
- **1 (POLY_PROXY)**: Magic Link users (requires exported private key)
- **2 (GNOSIS_SAFE)**: Multisig wallets

## WebSocket Subscription Format

### Subscribe to Market Data

```python
import json
import websocket

# After connecting to WebSocket
subscription_message = {
    "type": "subscribe",
    "channel": "market",  # or other topics
    "market": market_id,   # Optional filter
    "auth": {
        "apiKey": creds['apiKey'],
        "signature": generate_signature(),  # HMAC-SHA256
        "timestamp": int(time.time())
    }
}

ws.send(json.dumps(subscription_message))
```

### Available Topics

- `clob_market`: Price changes, orderbook, last trade price
- `clob_user`: User-specific orders and trades (requires auth)
- `activity`: Trades and matched orders
- `crypto_prices`: Real-time crypto price feeds

## Message Signature (HMAC-SHA256)

For L2 authentication, sign messages using HMAC-SHA256:

```python
import hmac
import hashlib
import base64

def generate_signature(timestamp, method, path, body, secret):
    """
    Generate HMAC-SHA256 signature for API requests

    Args:
        timestamp: Unix timestamp as string
        method: HTTP method (e.g., "GET", "POST")
        path: Request path
        body: Request body (empty string if none)
        secret: Base64-encoded secret from API credentials
    """
    # Decode base64 secret
    secret_bytes = base64.b64decode(secret)

    # Create message to sign
    message = f"{timestamp}{method}{path}{body}"

    # Generate HMAC signature
    signature = hmac.new(
        secret_bytes,
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()

    # Return base64-encoded signature
    return base64.b64encode(signature).decode('utf-8')
```

## Implementation in websocket_client.py

To enable authenticated WebSocket in the bot:

### 1. Generate API Credentials

First, generate and save credentials (do this once):

```python
from py_clob_client.client import ClobClient

client = ClobClient(
    "https://clob.polymarket.com",
    key=os.getenv("POLYMARKET_PRIVATE_KEY"),
    chain_id=137,
    signature_type=1,
    funder=os.getenv("POLYMARKET_WALLET_ADDRESS")
)

creds = client.create_or_derive_api_creds()

# Save to .env
print(f"POLYMARKET_API_KEY={creds['apiKey']}")
print(f"POLYMARKET_API_SECRET={creds['secret']}")
print(f"POLYMARKET_API_PASSPHRASE={creds['passphrase']}")
```

### 2. Update .env

Add credentials to `.env`:

```env
POLYMARKET_WALLET_ADDRESS=0xYourWalletAddress
POLYMARKET_PRIVATE_KEY=your_private_key_here
POLYMARKET_API_KEY=550e8400-e29b-41d4-a716-446655440000
POLYMARKET_API_SECRET=base64EncodedSecretString
POLYMARKET_API_PASSPHRASE=randomPassphraseString
```

### 3. Modify WebSocket Client

Update `websocket_client.py` to use authentication:

```python
class PolymarketWebSocketClient:
    def __init__(self, api_key=None, api_secret=None, api_passphrase=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        # ... rest of init

    def _send_subscription(self, market_id):
        timestamp = str(int(time.time()))
        signature = self._generate_signature(timestamp)

        subscription_message = {
            "type": "subscribe",
            "channel": "market",
            "market": market_id,
            "auth": {
                "apiKey": self.api_key,
                "signature": signature,
                "timestamp": timestamp,
                "passphrase": self.api_passphrase
            }
        }

        self.ws.send(json.dumps(subscription_message))
```

## Testing WebSocket Connection

Create a test script:

```python
# scripts_test/test_websocket_auth.py
import os
from websocket_client import PolymarketWebSocketClient

# Test connection
client = PolymarketWebSocketClient(
    api_key=os.getenv("POLYMARKET_API_KEY"),
    api_secret=os.getenv("POLYMARKET_API_SECRET"),
    api_passphrase=os.getenv("POLYMARKET_API_PASSPHRASE"),
    on_price_update=lambda mid, yp, np: print(f"{mid}: UP ${yp} | DOWN ${np}")
)

client.connect()
time.sleep(5)
client.subscribe("test-market-id")
time.sleep(60)  # Let it run for a minute
client.stop()
```

## Troubleshooting

### Connection Drops Immediately
- **Issue**: WebSocket connects then disconnects
- **Solution**: Ensure API credentials are valid and properly formatted

### "Unauthorized" Errors
- **Issue**: Subscription fails with 401/403
- **Solution**:
  - Regenerate API credentials
  - Check signature type matches your wallet
  - Verify timestamp is current (within 30 seconds)

### No Price Updates
- **Issue**: Connected but no messages received
- **Solution**:
  - Verify market ID is correct
  - Check subscription message format
  - Ensure market is active and not restricted

## Security Best Practices

1. **Never commit credentials**: Keep .env out of version control
2. **Rotate credentials**: Regenerate API credentials periodically
3. **Secure private key**: Use environment variables, never hardcode
4. **Limit permissions**: Only use necessary signature types
5. **Monitor usage**: Watch for unauthorized API calls

## Resources

- [Polymarket CLOB Authentication Docs](https://docs.polymarket.com/developers/CLOB/authentication)
- [py-clob-client GitHub](https://github.com/Polymarket/py-clob-client)
- [Real-Time Data Client](https://github.com/Polymarket/real-time-data-client)

## Current Status (in this repo)

❌ CLOB WebSocket (`wss://ws-subscriptions-clob.polymarket.com/ws/market`) - Connection drops immediately
❌ Public WebSocket (`wss://ws-live-data.polymarket.com`) - Connection drops immediately
✅ **REST API polling** - Working reliably (30-second interval)
✅ Auto-reconnect implemented in WebSocket client
✅ Fallback to REST API when WebSocket unavailable

**Findings from Testing**:
1. Both WebSocket endpoints reject subscriptions (with and without auth)
2. Credentials are loaded correctly from .env
3. Authentication signature generated using HMAC-SHA256
4. Server drops connection immediately after subscription attempt
5. Zero messages received before disconnect

**Possible Causes**:
1. API credentials may need different generation method
2. WebSocket subscription format may have changed
3. Endpoints may require additional authentication steps
4. Market data may only be available via REST API

**Current Solution**:
Using **REST API polling (every 30 seconds)** which is **sufficient for 15-minute markets**.
WebSocket disabled by default (`use_websocket=False` in btc_15min_bot.py:44)
