import requests
import json
from typing import List, Optional, Dict
from datetime import datetime
import logging
from strategies.base_strategy import Market, Trade

logger = logging.getLogger(__name__)


class PolymarketClient:
    """Client for interacting with Polymarket API"""

    def __init__(self, api_key: Optional[str] = None, private_key: Optional[str] = None):
        """
        Initialize Polymarket client

        Args:
            api_key: Polymarket API key (for authenticated requests)
            private_key: Private key for signing transactions
        """
        self.api_key = api_key
        self.private_key = private_key
        self.base_url = "https://gamma-api.polymarket.com"
        self.clob_url = "https://clob.polymarket.com"

    def get_markets(self, active_only: bool = True, limit: int = 100, max_markets: int = None) -> List[Market]:
        """
        Fetch all markets from Polymarket using pagination

        Args:
            active_only: Only return active markets
            limit: Number of markets to fetch per API request (max 100)
            max_markets: Maximum total markets to fetch (None = fetch all)

        Returns:
            List of Market objects
        """
        try:
            all_markets = []
            offset = 0
            batch_size = min(limit, 100)  # API max is 100 per request

            while True:
                # Fetch markets from Polymarket API
                url = f"{self.base_url}/markets"
                params = {
                    'limit': batch_size,
                    'offset': offset,
                    'closed': 'false'  # Don't fetch closed markets
                }
                if active_only:
                    params['active'] = 'true'

                logger.debug(f"Fetching markets with offset={offset}, limit={batch_size}")
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()

                markets_data = response.json()

                # No more markets to fetch
                if not markets_data or len(markets_data) == 0:
                    break

                logger.debug(f"Received {len(markets_data)} markets from API (offset={offset})")

                # Parse markets from this batch
                batch_markets = []
                for market_data in markets_data:
                    try:
                        market = self._parse_market(market_data)
                        if market:
                            batch_markets.append(market)
                    except Exception as e:
                        logger.debug(f"Failed to parse market {market_data.get('id', 'unknown')}: {e}")
                        continue

                all_markets.extend(batch_markets)

                # Check if we've reached the max_markets limit
                if max_markets and len(all_markets) >= max_markets:
                    all_markets = all_markets[:max_markets]
                    break

                # If we got fewer markets than requested, we've reached the end
                if len(markets_data) < batch_size:
                    break

                offset += batch_size

            logger.info(f"Fetched {len(all_markets)} valid markets from Polymarket (total API calls: {(offset // batch_size) + 1})")
            return all_markets

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch markets from Polymarket: {e}")
            return []

    def _parse_market(self, market_data: Dict) -> Optional[Market]:
        """Parse market data from API response"""
        try:
            # Skip closed or archived markets
            if market_data.get('closed', False) or market_data.get('archived', False):
                return None

            # Parse end date
            end_date_str = market_data.get('endDate')
            if not end_date_str:
                logger.debug(f"Market {market_data.get('id')} missing end date")
                return None

            # Handle different date formats - always return timezone-naive datetime
            if 'T' in end_date_str:
                # Parse ISO format and convert to timezone-naive UTC
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                if end_date.tzinfo is not None:
                    # Convert to UTC then remove timezone info
                    end_date = end_date.replace(tzinfo=None)
            else:
                # If it's just a date, assume end of day UTC
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

            # Check if market is in the future (both datetimes are timezone-naive UTC)
            now_utc = datetime.utcnow()
            if end_date < now_utc:
                return None

            # Parse outcomes and prices (they are JSON strings in the API)
            yes_price = 0.0
            no_price = 0.0

            # Try to parse outcomePrices (it's a JSON string like "[\"0.7\", \"0.3\"]")
            outcome_prices_str = market_data.get('outcomePrices', '[]')
            try:
                if isinstance(outcome_prices_str, str):
                    outcome_prices = json.loads(outcome_prices_str)
                else:
                    outcome_prices = outcome_prices_str

                if len(outcome_prices) >= 2:
                    yes_price = float(outcome_prices[0])
                    no_price = float(outcome_prices[1])
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                logger.debug(f"Could not parse outcome prices for market {market_data.get('id')}: {e}")

            # If outcomePrices didn't work, try bestBid/bestAsk
            if yes_price == 0.0 and no_price == 0.0:
                yes_price = float(market_data.get('bestBid', 0))
                no_price = float(market_data.get('bestAsk', 0))

            # Get volume (use volumeNum which is the numeric field)
            volume = float(market_data.get('volumeNum', 0))

            # Check if this is truly an active market with prices
            is_active = (
                market_data.get('active', False) and
                not market_data.get('closed', False) and
                (yes_price > 0 or no_price > 0)
            )

            if not is_active:
                return None

            return Market(
                id=market_data.get('id', ''),
                question=market_data.get('question', ''),
                end_date=end_date,
                yes_price=yes_price,
                no_price=no_price,
                volume=volume,
                active=is_active
            )

        except Exception as e:
            logger.error(f"Error parsing market data: {e}")
            return None

    def execute_trade(self, trade: Trade) -> bool:
        """
        Execute a trade on Polymarket

        Args:
            trade: Trade object to execute

        Returns:
            True if trade was successful, False otherwise
        """
        try:
            logger.info(f"EXECUTING TRADE: {trade.side} {trade.amount} shares of '{trade.question}' at ${trade.price:.2f}")
            logger.info(f"Reason: {trade.reason}")

            if not self.private_key:
                logger.warning("No private key configured - SIMULATED TRADE ONLY")
                return True

            # Here you would implement actual trade execution using py-clob-client
            # For now, this is a placeholder that logs the trade
            # You'll need to:
            # 1. Create an order using the CLOB API
            # 2. Sign the order with your private key
            # 3. Submit the order

            logger.info(f"Trade would be executed: {trade}")
            return True

        except Exception as e:
            logger.error(f"Failed to execute trade: {e}")
            return False

    def get_market_by_id(self, market_id: str) -> Optional[Market]:
        """Fetch a specific market by ID"""
        try:
            url = f"{self.base_url}/markets/{market_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            market_data = response.json()
            return self._parse_market(market_data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch market {market_id}: {e}")
            return None

    def get_btc_15min_markets(self, num_future_markets: int = 4) -> List[Market]:
        """
        Fetch Bitcoin 15-minute UP/DOWN markets by generating slugs

        These markets have slugs like: btc-updown-15m-{start_timestamp}
        where start_timestamp is the START time of the 15-min window.
        Markets are created every 15 minutes (900 seconds apart).

        Args:
            num_future_markets: Number of future markets to check (default: 4)

        Returns:
            List of active BTC 15-min markets
        """
        try:
            from datetime import datetime, timedelta

            now = datetime.utcnow()
            markets = []

            # Round down to nearest 15-minute interval
            minutes = (now.minute // 15) * 15
            current_interval = now.replace(minute=minutes, second=0, microsecond=0)

            logger.debug(f"Current time: {now}")
            logger.debug(f"Current 15-min interval: {current_interval}")

            # Check previous, current, and next N markets
            for i in range(-1, num_future_markets + 1):
                interval_time = current_interval + timedelta(minutes=15 * i)
                timestamp = int(interval_time.timestamp())
                slug = f"btc-updown-15m-{timestamp}"

                try:
                    # Fetch market by slug
                    url = f"{self.base_url}/markets"
                    params = {'slug': slug, 'limit': 1}

                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()

                    markets_data = response.json()

                    if markets_data and len(markets_data) > 0:
                        market_data = markets_data[0]

                        # Check if it's active and not closed
                        if market_data.get('active') and not market_data.get('closed'):
                            market = self._parse_market(market_data)
                            if market:
                                markets.append(market)
                                logger.debug(f"Found active market: {slug}")
                        else:
                            logger.debug(f"Market {slug} exists but is closed/inactive")
                    else:
                        logger.debug(f"Market {slug} not found (may not be created yet)")

                except requests.exceptions.RequestException as e:
                    logger.debug(f"Error fetching {slug}: {e}")
                    continue

            logger.info(f"Found {len(markets)} active BTC 15-min markets")
            return markets

        except Exception as e:
            logger.error(f"Failed to fetch BTC markets: {e}")
            return []
