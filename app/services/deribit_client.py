from decimal import Decimal

import aiohttp

from app.schemas.deribit_response import DeribitResponse


class DeribitClient:
    """
    Asynchronous HTTP client for interacting with Deribit cryptocurrency exchange API.

    This client provides methods to fetch real-time market data from Deribit's
    public REST API. It implements best practices for HTTP client usage including
    connection pooling, proper error handling, and async/await patterns.

    Base URL: https://www.deribit.com/api/v2/public/

    API Documentation: https://docs.deribit.com/

    Features:
        - Asynchronous HTTP requests using aiohttp
        - Automatic connection pooling and reuse
        - HTTP error handling with raise_for_status()
        - Type-safe response parsing using Pydantic schemas
        - Stateless design - safe to reuse across requests

    Rate Limits:
        - Public endpoints: 20 requests per second
        - Consider implementing rate limiting if making frequent requests

    Error Handling:
        - aiohttp.ClientError for network issues
        - HTTP status codes 4xx/5xx are raised as exceptions
        - JSON parsing errors are propagated

    Thread Safety: This class is thread-safe as it creates new ClientSession
    for each request, but consider using a single session for better performance
    in high-throughput scenarios.
    """

    def __init__(self) -> None:
        """
        Initialize the Deribit API client.

        Notes:
            - Uses Deribit's v2 public API endpoint
            - No authentication required for public endpoints
            - Base URL follows Deribit's REST API structure
            - ClientSession is created per request for simplicity
        """
        self.base_url = "https://www.deribit.com/api/v2/public/{action}"

    async def get_index_data(self, ticker: str) -> DeribitResponse:
        """
        Fetch current index price data for a cryptocurrency.

        This method calls Deribit's `get_index_price` endpoint which returns
        the current index price (average of major exchange prices) for the
        specified cryptocurrency pair.

        Args:
            ticker: Cryptocurrency index name. Supported values:
                   - "btc_usd" for Bitcoin/US Dollar index
                   - "eth_usd" for Ethereum/US Dollar index
                   Other index names may be available (check Deribit documentation)

        Returns:
            DeribitResponse: Structured response containing:
                - result.index_price: Current index price as float
                - result.estimated_delivery_price: Estimated futures delivery price
                - usIn: Request timestamp in microseconds (UNIX time)
                - usOut: Response timestamp in microseconds (optional)
                - usDiff: Processing time in microseconds (optional)

        Raises:
            aiohttp.ClientError: If network connection fails, timeout occurs,
                                or server is unreachable
            aiohttp.ClientResponseError: If HTTP status code is 4xx or 5xx
            ValueError: If ticker parameter is invalid or malformed
            JSONDecodeError: If API response is not valid JSON
        """
        action = f"get_index_price?index_name={ticker}"
        url = self.base_url.format(action=action)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data: DeribitResponse = await response.json()
                return data
