from collections.abc import Sequence
from typing import Optional, cast

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.currency_price import CurrencyPrice


class DeribitRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_price(self, ticker: str, price: float, timestamp: int) -> None:
        new_entry = CurrencyPrice(ticker=ticker, price=price, timestamp=timestamp)
        self.session.add(new_entry)
        await self.session.commit()

    async def get_all_by_ticker(self, ticker: str) -> Sequence[CurrencyPrice]:
        stmt = select(CurrencyPrice).where(CurrencyPrice.ticker == ticker)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest(self, ticker: str) -> CurrencyPrice | None:
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
        Получение цен с фильтрацией по временному диапазону (UNIX timestamp).
        """
        stmt = select(CurrencyPrice).where(CurrencyPrice.ticker == ticker)

        if start_ts is not None:
            stmt = stmt.where(CurrencyPrice.timestamp >= start_ts)

        if end_ts is not None:
            stmt = stmt.where(CurrencyPrice.timestamp <= end_ts)

        stmt = stmt.order_by(CurrencyPrice.timestamp.asc())

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
