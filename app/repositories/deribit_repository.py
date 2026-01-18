from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.currency_price import CurrencyPrice


class DeribitRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_price(self, ticker: str, price: float, timestamp: int):
        new_entry = CurrencyPrice(ticker=ticker, price=price, timestamp=timestamp)
        self.session.add(new_entry)
        await self.session.commit()

    async def get_all_by_ticker(self, ticker: str):
        stmt = select(CurrencyPrice).where(CurrencyPrice.ticker == ticker)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_latest(self, ticker: str):
        stmt = (
            select(CurrencyPrice)
            .where(CurrencyPrice.ticker == ticker)
            .order_by(CurrencyPrice.timestamp.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_range(self, ticker: str, start_ts: int = None, end_ts: int = None):
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
        return result.scalars().all()
