# Getting Started with Polymarket

This guide will help you understand Polymarket, create an account, and get API credentials for automated trading.

## Table of Contents
- [What is Polymarket?](#what-is-polymarket)
- [How Polymarket Works](#how-polymarket-works)
- [Creating an Account](#creating-an-account)
- [Getting Your API Credentials](#getting-your-api-credentials)
- [Understanding Polymarket Markets](#understanding-polymarket-markets)
- [Fees and Costs](#fees-and-costs)
- [Trading Basics](#trading-basics)
- [Important Concepts](#important-concepts)
- [Resources](#resources)

## What is Polymarket?

Polymarket is a decentralized information markets platform where users can trade on the outcomes of real-world events. It's built on the Polygon blockchain and uses USDC (a stablecoin pegged to the US dollar) for all transactions.

### Key Facts

- **Blockchain**: Built on Polygon (Ethereum Layer 2)
- **Currency**: USDC only (1 USDC = $1 USD)
- **Market Type**: Binary outcome prediction markets (YES/NO)
- **Trading**: Central Limit Order Book (CLOB) exchange
- **Resolution**: Markets resolve based on real-world outcomes
- **Regulatory**: Available globally (with some restrictions)

## How Polymarket Works

### Prediction Markets

Polymarket uses **binary outcome markets** - each market has exactly two outcomes:
- **YES** - The event will happen
- **NO** - The event will not happen

### Shares and Pricing

- Each share is priced between $0.00 and $1.00
- The price represents the market's probability of that outcome
- Example: YES shares at $0.75 means the market believes there's a 75% chance the event will happen
- YES price + NO price should always equal approximately $1.00 (minus fees/spread)

### How Trading Works

1. **Buy Shares**: Purchase YES or NO shares at current market price
2. **Hold Until Resolution**: Wait for the event to occur and market to resolve
3. **Settlement**:
   - Winning shares pay out $1.00 each
   - Losing shares are worth $0.00
   - Profit = ($1.00 - purchase price) × number of shares

### Example Trade

```
Market: "Will it rain in NYC tomorrow?"
YES price: $0.70 (70% probability)
NO price: $0.30 (30% probability)

If you buy 10 YES shares at $0.70:
- Cost: 10 × $0.70 = $7.00 USDC
- If it rains: You receive 10 × $1.00 = $10.00 USDC
- Profit: $10.00 - $7.00 = $3.00 USDC (42.8% return)
- If it doesn't rain: You receive $0.00 (lose your $7.00)
```

## Creating an Account

### Step 1: Visit Polymarket

1. Go to [https://polymarket.com](https://polymarket.com)
2. Click "Sign In" or "Get Started" in the top right corner

### Step 2: Create Your Wallet

Polymarket supports multiple wallet options:

**Option A: Email Sign-Up (Easiest)**
1. Click "Continue with Email"
2. Enter your email address
3. Verify your email
4. Polymarket creates a wallet for you automatically

**Option B: Connect Existing Wallet**
1. Click "Connect Wallet"
2. Choose your wallet provider:
   - MetaMask (most popular)
   - WalletConnect
   - Coinbase Wallet
   - Other Web3 wallets
3. Follow the prompts to connect

**Option C: Use Polymarket Wallet (Recommended for Trading Bot)**
1. Download the Polymarket mobile app or use their web wallet
2. Create a new wallet
3. **IMPORTANT**: Save your recovery phrase securely
4. Set up a password

### Step 3: Fund Your Account

1. Navigate to your wallet/profile
2. Click "Deposit" or "Add Funds"
3. Deposit USDC (options vary by region):
   - **Credit/Debit Card**: Direct purchase (fees apply)
   - **Crypto Transfer**: Send USDC from another wallet
   - **Bridge**: Bridge USDC from Ethereum mainnet
   - **Exchange**: Buy on exchange and transfer

**Minimum Deposit**: No strict minimum, but start with at least $10-20 USDC for testing

### Step 4: Verify Your Account (May Be Required)

Depending on your location and trading volume:
1. Go to Account Settings
2. Complete KYC (Know Your Customer) verification
3. Provide identification documents if requested
4. Wait for verification approval

## Getting Your API Credentials

### Understanding Polymarket API Access

Polymarket has two main APIs:
1. **Gamma API**: Public market data (no auth required)
2. **CLOB API**: Trading and order management (requires authentication)

### For Automated Trading (CLOB API)

**Step 1: Export Your Private Key**

Your private key is needed to sign transactions. How you get it depends on your wallet:

**If Using Polymarket Email Wallet:**
1. Log in to Polymarket
2. Go to Settings → Security
3. Click "Export Private Key"
4. Enter your password
5. Copy your private key
6. **CRITICAL**: Store this securely - never share it!

**If Using MetaMask:**
1. Click the three dots next to your account
2. Select "Account Details"
3. Click "Export Private Key"
4. Enter your MetaMask password
5. Copy the private key shown

**If Using Mobile Wallet:**
1. Go to Settings → Security
2. Look for "Export Private Key" or "Show Private Key"
3. Authenticate and copy the key

**Step 2: Set Up API Key (Optional)**

For read-only data, no API key is needed. For advanced features:
1. Log in to Polymarket
2. Navigate to Settings → API or Developer Settings
3. Click "Generate API Key"
4. Name your key (e.g., "Trading Bot")
5. Copy and save the API key securely

**Step 3: Configure Your Trading Bot**

Add to your `.env` file:
```env
POLYMARKET_PRIVATE_KEY=0x1234567890abcdef...  # Your private key
POLYMARKET_API_KEY=your_api_key_here          # If you have one
```

### Security Best Practices

⚠️ **CRITICAL SECURITY WARNINGS**:
- Never commit your private key to Git
- Never share your private key with anyone
- Use a dedicated wallet for bot trading (separate from main funds)
- Start with small amounts when testing
- Keep most funds in a separate, secure wallet
- Consider using a hardware wallet for long-term storage

## Understanding Polymarket Markets

### Market Lifecycle

1. **Creation**: Market is created with a question and resolution criteria
2. **Trading**: Users buy and sell YES/NO shares
3. **End Date**: Trading may continue after the event occurs
4. **Resolution**: Outcome is determined based on resolution source
5. **Settlement**: Winning shares pay $1.00, losing shares pay $0.00

### Resolution Sources

Markets resolve based on predetermined sources:
- **Official Sources**: Government data, company announcements
- **News Outlets**: Major news organizations (NYT, Reuters, etc.)
- **UMA Protocol**: Decentralized oracle for disputed resolutions
- **Specific Criteria**: Clearly defined in market rules

### Market Information

Each market displays:
- **Question**: The event being predicted
- **End Date**: When the event should occur by
- **Resolution Source**: How the outcome will be determined
- **Volume**: Total USDC traded
- **Liquidity**: Available orders in the order book
- **Current Prices**: YES and NO share prices

### Example Market Breakdown

```
Question: "Will Bitcoin be above $50,000 on December 31, 2024?"
End Date: December 31, 2024, 11:59 PM UTC
Resolution Source: Coinbase BTC-USD price at 11:59 PM UTC
Volume: $2,456,789
YES Price: $0.62 (62% probability)
NO Price: $0.38 (38% probability)
```

## Fees and Costs

### Trading Fees

Polymarket charges fees in two ways:

**1. Trading Fees**
- **Maker Fee**: ~0% (sometimes rebates for adding liquidity)
- **Taker Fee**: ~2% (for removing liquidity)
- Fees are automatically included in prices

**2. Network Fees (Gas)**
- Built on Polygon (very low fees)
- Typical transaction: $0.01 - $0.10
- Much cheaper than Ethereum mainnet

### Other Costs

- **Deposit Fees**: Vary by method (credit card ~2-4%, crypto transfer minimal)
- **Withdrawal Fees**: Small network fee for crypto transfers
- **Spread**: Difference between buy and sell prices (market dependent)

### Fee Example

```
Buying 100 YES shares at $0.70:
- Share Cost: 100 × $0.70 = $70.00
- Trading Fee: ~$1.40 (2% taker fee)
- Gas Fee: ~$0.05 (Polygon network)
- Total Cost: ~$71.45

If YES wins:
- Payout: 100 × $1.00 = $100.00
- Profit: $100.00 - $71.45 = $28.55
```

## Trading Basics

### Order Types

**1. Market Order**
- Buys/sells immediately at current best price
- Guaranteed execution
- You pay the taker fee
- Best for: Quick execution, liquid markets

**2. Limit Order**
- Sets your desired price
- Only executes at that price or better
- May not execute immediately
- You pay the maker fee (or get rebate)
- Best for: Better prices, patient trading

### Trading Strategies (Manual)

**1. Long Position (Buying)**
- Buy YES if you think the event will happen
- Buy NO if you think it won't happen
- Profit if you're correct

**2. Selling Shares**
- Sell shares you own before market resolves
- Lock in profits or cut losses
- Creates liquidity for other traders

**3. Holding to Resolution**
- Keep shares until market resolves
- Maximum profit if correct
- Risk of total loss if wrong

### Order Book Mechanics

The Central Limit Order Book (CLOB) works like a stock exchange:

```
Order Book Example:

YES Shares:
Bids (Buy)          Asks (Sell)
$0.69 - 100 shares  $0.71 - 150 shares
$0.68 - 200 shares  $0.72 - 100 shares
$0.67 - 150 shares  $0.73 - 200 shares

Spread: $0.71 - $0.69 = $0.02
```

## Important Concepts

### Liquidity

- **High Liquidity**: Easy to buy/sell, tight spreads, stable prices
- **Low Liquidity**: Harder to trade, wide spreads, price slippage
- Check volume and order book depth before trading

### Implied Probability

Share price = Market's estimated probability
- $0.75 YES = 75% chance of occurring
- $0.25 NO = 25% chance (inverse of above)
- Prices reflect collective wisdom of all traders

### Market Efficiency

- Popular markets tend to be more efficient (accurate)
- Niche markets may have inefficiencies (opportunities)
- New information moves prices quickly
- Consider why you might know something the market doesn't

### Risk Management

**Key Risks:**
1. **Event Risk**: The outcome you bet against occurs
2. **Resolution Risk**: Market resolves differently than expected
3. **Liquidity Risk**: Can't exit position at fair price
4. **Smart Contract Risk**: Technical issues (rare but possible)
5. **Regulatory Risk**: Legal changes affecting platform

**Risk Mitigation:**
- Diversify across multiple markets
- Only trade what you can afford to lose
- Understand resolution criteria clearly
- Use limit orders in low-liquidity markets
- Keep some funds liquid for opportunities

### Arbitrage Opportunities

Sometimes inefficiencies exist:
- YES + NO ≠ $1.00 (account for fees)
- Same event, different markets
- Correlated markets with inconsistent prices

**Note**: True arbitrage is rare and requires:
- Fast execution
- Sufficient liquidity
- Careful fee calculation
- Understanding of resolution criteria

## Advanced Topics

### API Trading Considerations

When using the trading bot:
- **Rate Limits**: Don't spam API requests
- **Slippage**: Prices can move between seeing and executing
- **Order Matching**: Understand maker vs taker
- **Position Sizing**: Calculate including fees
- **Market Impact**: Large orders move prices

### Using the CLOB Client

For production trading, you'll need `py-clob-client`:

```python
from py_clob_client.client import ClobClient

# Initialize client
client = ClobClient(
    host="https://clob.polymarket.com",
    key=your_private_key,
    chain_id=137  # Polygon mainnet
)

# Place order
order = client.create_order({
    "tokenID": "...",
    "price": 0.75,
    "size": 10,
    "side": "BUY"
})
```

### Polygon Network Setup

Your wallet needs to be configured for Polygon:
- **Network Name**: Polygon Mainnet
- **RPC URL**: https://polygon-rpc.com
- **Chain ID**: 137
- **Currency**: MATIC (for gas fees, though minimal)
- **Block Explorer**: https://polygonscan.com

## Resources

### Official Polymarket Resources

- **Website**: https://polymarket.com
- **Help Center**: https://polymarket.com/help
- **Discord**: Join for community support
- **Twitter/X**: @Polymarket for updates
- **Blog**: https://polymarket.com/blog

### API Documentation

- **Gamma API Docs**: https://docs.polymarket.com (public data)
- **CLOB API Docs**: https://docs.polymarket.com/api (trading)
- **GitHub**: https://github.com/Polymarket (official repos)
- **py-clob-client**: Python library for trading

### Learning Resources

- **Polymarket Knowledge Base**: Detailed guides and FAQs
- **YouTube**: Tutorial videos on prediction markets
- **Community**: Discord and Reddit for questions

### Market Analysis Tools

- **Polymarket Pro**: Advanced charting (if available)
- **External Trackers**: Third-party analytics sites
- **API**: Build your own analysis tools

### Blockchain Explorers

- **Polygonscan**: https://polygonscan.com (transaction history)
- **Your Wallet**: View all transactions and balances

## Troubleshooting

### Common Issues

**"Can't connect wallet"**
- Ensure wallet is set to Polygon network
- Clear browser cache
- Try different browser/wallet

**"Insufficient funds"**
- Check USDC balance (not MATIC)
- Account for fees in calculations
- Ensure funds are on Polygon, not Ethereum mainnet

**"Transaction failed"**
- Check gas fees (need small amount of MATIC)
- Ensure enough USDC for trade + fees
- Network might be congested (rare on Polygon)

**"Market not found" (API)**
- Market may have ended
- Check market ID is correct
- API endpoint might have changed

### Getting Help

1. Check Polymarket Help Center
2. Ask in Discord community
3. Contact Polymarket support
4. Review API documentation
5. Check GitHub issues for known problems

## Safety Checklist

Before you start trading:

- [ ] Understand how prediction markets work
- [ ] Know what you're betting on (read market rules carefully)
- [ ] Have secured your private key safely
- [ ] Started with a small test amount
- [ ] Configured `.env` file correctly
- [ ] Tested in DRY_RUN mode first
- [ ] Understand all fees involved
- [ ] Know how to withdraw funds
- [ ] Have a risk management plan
- [ ] Never invest more than you can afford to lose

## Next Steps

1. **Create your account** on Polymarket
2. **Fund with small amount** ($10-20 USDC) for testing
3. **Make a manual trade** to understand the process
4. **Export your private key** securely
5. **Configure the trading bot** with credentials
6. **Run in dry-run mode** to test strategies
7. **Monitor and adjust** based on results
8. **Scale gradually** as you gain confidence

---

**Disclaimer**: This guide is for educational purposes. Trading on prediction markets involves risk. Always do your own research and never invest more than you can afford to lose. Polymarket's terms of service and local regulations apply.

**Last Updated**: December 2024 - Always check official Polymarket documentation for the most current information.
