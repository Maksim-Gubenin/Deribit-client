from collections.abc import Sequence
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.currency_price import CurrencyPrice
from app.repositories import DeribitRepository
from app.services.deribit_client import DeribitClient


class DeribitService:
    """
    Service layer for Deribit cryptocurrency price operations.

    This class orchestrates business logic between the API client,
    database repository, and application layers. It provides methods
    for fetching current prices from Deribit API and retrieving
    historical data from the database.

    Responsibilities:
        - Fetch current index prices from Deribit API
        - Save price data to the database
        - Retrieve historical price data with various filters
        - Handle business logic and data transformation

    Design Pattern: Service Layer Pattern
    - Separates business logic from data access (repository)
    - Provides a clean API for the application layer
    - Centralizes price-related operations

    Dependencies:
        - DeribitClient: For external API communication
        - DeribitRepository: For database operations

    Thread Safety: This class is not thread-safe; create new instance per request.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize DeribitService with database session.

        Args:
            session: SQLAlchemy async session for database operations.
                   Should be provided by dependency injection (FastAPI/SessionDep).

        Notes:
            - Creates fresh repository and client instances for each service instance
            - The session lifecycle is managed by the caller (FastAPI/Celery task)
            - Repository and client are stateless and safe to reuse
        """
        self.repo = DeribitRepository(session)
        self.client = DeribitClient()

    async def collect_and_save_prices(self, ticker: str) -> None:
        """
        Fetch current price from Deribit API and save to database.

        This method performs the core business logic:
        1. Fetches current index price from Deribit API
        2. Extracts price and timestamp from API response
        3. Saves the data to the database via repository

        Args:
            ticker: Cryptocurrency ticker symbol (e.g., "btc_usd", "eth_usd")

        Returns:
            None: Price is saved to database as a side effect

        Raises:
            aiohttp.ClientError: If API request fails (network issues, timeout)
            KeyError: If API response format is unexpected
            sqlalchemy.exc.SQLAlchemyError: If database operation fails
        """
        data = await self.client.get_index_data(ticker=ticker)

        price = float(data["result"]["index_price"])
        time_in_data = int(data["usIn"])

        await self.repo.add_price(ticker=ticker, price=price, timestamp=time_in_data)

    async def get_prices_with_by_date(
        self, ticker: str, start_ts: int | None = None, end_ts: int | None = None
    ) -> Sequence[CurrencyPrice]:
        """
        Get price records filtered by date range.

        Retrieves historical price data for a specific ticker within
        the specified time range (inclusive). Both start and end timestamps
        are optional - omitting them removes that side of the filter.

        Args:
            ticker: Cryptocurrency ticker symbol (e.g., "btc_usd", "eth_usd")
            start_ts: Start timestamp in microseconds (inclusive, optional)
            end_ts: End timestamp in microseconds (inclusive, optional)

        Returns:
            Sequence[CurrencyPrice]: List of price records sorted by timestamp ascending
        """
        return await self.repo.get_by_range(
            ticker=ticker, start_ts=start_ts, end_ts=end_ts
        )

    async def get_prices_by_all_date(self, ticker: str) -> Sequence[CurrencyPrice]:
        """
        Get all historical price records for a ticker.

        Retrieves complete price history for the specified cryptocurrency,
        sorted by timestamp in ascending order (oldest to newest).

        Args:
            ticker: Cryptocurrency ticker symbol (e.g., "btc_usd", "eth_usd")

        Returns:
            Sequence[CurrencyPrice]: All price records for the ticker

        Notes:
            - For large datasets, consider pagination or date filtering
            - Returns empty sequence if no records found
        """
        return await self.repo.get_all_by_ticker(ticker)

    async def get_last_known_price(self, ticker: str) -> CurrencyPrice | None:
        """
        Get the most recent price record for a ticker.

        Useful for getting current market price or checking if data exists.
        Returns None if no prices are found for the specified ticker.

        Args:
            ticker: Cryptocurrency ticker symbol (e.g., "btc_usd", "eth_usd")

        Returns:
            CurrencyPrice | None: Latest price record or None if not found

        Performance:
            - Uses database index on (ticker, timestamp) for efficient query
            - Returns single record regardless of data volume
        """
        return await self.repo.get_latest(ticker)
