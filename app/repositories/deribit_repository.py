from collections.abc import Sequence
from typing import Optional, cast

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.currency_price import CurrencyPrice


class DeribitRepository:
    """
    Repository pattern implementation for cryptocurrency price data access.

    This class encapsulates all database operations related to CurrencyPrice
    entities, providing a clean abstraction layer between the business logic
    (service layer) and the data persistence layer (SQLAlchemy).
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize repository with a database session.

        Args:
            session: SQLAlchemy async session for database operations.
                   Should be provided by the service layer or dependency injection.
        """
        self.session = session

    async def add_price(self, ticker: str, price: float, timestamp: int) -> None:
        """
        Create and persist a new price record.

        Inserts a new CurrencyPrice entity into the database with an immediate
        commit. This ensures data durability but may impact performance in
        high-frequency scenarios.

        Args:
            ticker: Cryptocurrency pair identifier (e.g., "btc_usd", "eth_usd")
            price: Current index price as floating-point number.
                  Note: Stored as DECIMAL(20,8) in database for precision.
            timestamp: UNIX timestamp in microseconds when price was recorded.

        Returns:
            None: Operation completes when record is successfully committed.

        """
        new_entry = CurrencyPrice(ticker=ticker, price=price, timestamp=timestamp)
        self.session.add(new_entry)
        await self.session.commit()

    async def get_all_by_ticker(self, ticker: str) -> Sequence[CurrencyPrice]:
        """
        Retrieve all price records for a specific cryptocurrency ticker.

        Fetches complete price history for the given ticker, sorted by
        timestamp in ascending order (oldest to newest). Returns empty
        list if no records found.

        Args:
            ticker: Cryptocurrency pair identifier (e.g., "btc_usd", "eth_usd")

        Returns:
            Sequence[CurrencyPrice]: List of all price records for the ticker,
                                    ordered by timestamp ascending.
        """
        stmt = select(CurrencyPrice).where(CurrencyPrice.ticker == ticker)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest(self, ticker: str) -> CurrencyPrice | None:
        """
        Retrieve the most recent price record for a ticker.

        Fetches the single latest (most recent) price record based on
        timestamp. Returns None if no prices exist for the ticker.

        Args:
            ticker: Cryptocurrency pair identifier (e.g., "btc_usd", "eth_usd")

        Returns:
            CurrencyPrice | None: Latest price record or None if not found.6
        """
        stmt = (
            select(CurrencyPrice)
            .where(CurrencyPrice.ticker == ticker)
            .order_by(CurrencyPrice.timestamp.desc())
            .limit(1)
        )
        result: Result = await self.session.execute(stmt)
        return cast(CurrencyPrice | None, result.scalar_one_or_none())

    async def get_by_range(
        self, ticker: str, start_ts: int | None = None, end_ts: int | None = None
    ) -> Sequence[CurrencyPrice]:
        """
        Retrieve price records filtered by timestamp range.

        Fetches price records for a specific ticker within an optional
        time range (inclusive). Both start and end timestamps are optional.
        Results are ordered chronologically (oldest to newest).

        Args:
            ticker: Cryptocurrency pair identifier (e.g., "btc_usd", "eth_usd")
            start_ts: Optional start timestamp in microseconds (inclusive).
                     If None, no lower bound is applied.
            end_ts: Optional end timestamp in microseconds (inclusive).
                   If None, no upper bound is applied.

        Returns:
            Sequence[CurrencyPrice]: Price records within the specified range,
                                    ordered by timestamp ascending.
        """
        stmt = select(CurrencyPrice).where(CurrencyPrice.ticker == ticker)

        if start_ts is not None:
            stmt = stmt.where(CurrencyPrice.timestamp >= start_ts)

        if end_ts is not None:
            stmt = stmt.where(CurrencyPrice.timestamp <= end_ts)

        stmt = stmt.order_by(CurrencyPrice.timestamp.asc())

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
