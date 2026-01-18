from fastapi import APIRouter, Query

from app.core.dependencies import SessionDep
from app.schemas.price import PriceList, PriceRead
from app.services import DeribitService

router = APIRouter()


@router.get("/", response_model=PriceList)
async def get_prices_by_ticker(
    session: SessionDep,
    ticker: str = Query(..., description="Тикер валюты: btc_usd или eth_usd"),
) -> PriceList:
    service = DeribitService(session=session)
    currency_prices = await service.get_prices_by_all_date(ticker=ticker)

    if not currency_prices:
        return PriceList(items=[])

    items = [PriceRead.model_validate(price) for price in currency_prices]

    return PriceList(items=items)
