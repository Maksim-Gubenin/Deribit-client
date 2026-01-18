import aiohttp
from decimal import Decimal

class DeribitClient:
    def __init__(self):
        self.base_url = "https://www.deribit.com/api/v2/public/{action}"

    async def get_index_data(self, ticker: str) -> dict:
        action = "get_index_price?index_name={ticker}".format(ticker=ticker)
        url = self.base_url.format(action=action)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                return data
