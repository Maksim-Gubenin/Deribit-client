from collections.abc import Sequence
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.currency_price import CurrencyPrice
from app.repositories import DeribitRepository
from app.services.deribit_client import DeribitClient


class DeribitService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = DeribitRepository(session)
        self.client = DeribitClient()

    async def collect_and_save_prices(self, ticker: str) -> None:
        data = await self.client.get_index_data(ticker=ticker)
        price = float(data["result"]["index_price"])
        time_in_data = int(data["usIn"])
        await self.repo.add_price(ticker=ticker, price=price, timestamp=time_in_data)

    async def get_prices_with_by_date(
        self, ticker: str, start_ts: int | None = None, end_ts: int | None = None
    ) -> Sequence[CurrencyPrice]:
        return await self.repo.get_by_range(
            ticker=ticker, start_ts=start_ts, end_ts=end_ts
        )

    async def get_prices_by_all_date(self, ticker: str) -> Sequence[CurrencyPrice]:
        return await self.repo.get_all_by_ticker(ticker)

    async def get_last_known_price(self, ticker: str) -> CurrencyPrice | None:
        return await self.repo.get_latest(ticker)
