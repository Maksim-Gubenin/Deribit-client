from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import DeribitRepository
from app.services.deribit_client import DeribitClient
from app.core.models.currency_price import CurrencyPrice


class DeribitService:
    def __init__(self, session: AsyncSession):
        self.repo = DeribitRepository(session)
        self.client = DeribitClient()

    async def collect_and_save_prices(self, ticker: str) -> None:
        data = await self.client.get_index_data(ticker=ticker)
        price = float(data["result"]["index_price"])
        time_in_data = int(data["time_in_data"])
        await self.repo.add_price(
            ticker=ticker,
            price=price,
            timestamp=time_in_data
        )

    async def get_filtered_prices(
        self,
        ticker: str,
        start_ts: Optional[int],
        end_ts: Optional[int]
    ) -> list[CurrencyPrice]:
        if start_ts or end_ts:
            return await self.repo.get_by_range(
                ticker=ticker,
                start_ts=start_ts,
                end_ts=end_ts)
        return await self.repo.get_all_by_ticker(ticker)

    async def get_last_known_price(self, ticker: str) -> Optional[CurrencyPrice]:
        return await self.repo.get_latest(ticker)
