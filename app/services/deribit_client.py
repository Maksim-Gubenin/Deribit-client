from decimal import Decimal

import aiohttp

from app.schemas.deribit_response import DeribitResponse


class DeribitClient:
    def __init__(self) -> None:
        self.base_url = "https://www.deribit.com/api/v2/public/{action}"

    async def get_index_data(self, ticker: str) -> DeribitResponse:
        action = f"get_index_price?index_name={ticker}"
        url = self.base_url.format(action=action)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data: DeribitResponse = await response.json()
                return data
