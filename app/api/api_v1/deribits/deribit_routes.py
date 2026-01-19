from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from app.core.dependencies import SessionDep
from app.schemas.price import PriceList, PriceRead
from app.services import DeribitService

router = APIRouter()


@router.get("/", response_model=PriceList)
async def get_all_prices(
    session: SessionDep,
    ticker: str = Query(..., description="Currency ticker: btc_usd or eth_usd"),
) -> PriceList:
    """
    Get all historical price data for a specified currency ticker.

    This endpoint returns all saved price records for the given cryptocurrency ticker.
    The data is collected periodically from Deribit exchange and stored in the database.

    Args:
        session: Database session dependency
        ticker: Currency ticker symbol. Must be either 'btc_usd' or 'eth_usd'

    Returns:
        PriceList: List of all price records for the specified ticker

    Raises:
        HTTPException: 400 - If ticker is not 'btc_usd' or 'eth_usd'

    Examples:
        ```bash
        # Get all BTC prices
        curl -X GET "http://localhost:8000/api/prices/?ticker=btc_usd"

        # Get all ETH prices
        curl -X GET "http://localhost:8000/api/prices/?ticker=eth_usd"
        ```
    """
    if ticker not in ["btc_usd", "eth_usd"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid ticker. Allowed values: btc_usd, eth_usd",
        )

    service = DeribitService(session=session)
    currency_prices = await service.get_prices_by_all_date(ticker=ticker)

    items = [PriceRead.model_validate(price) for price in currency_prices]
    return PriceList(items=items)


@router.get("/latest", response_model=PriceRead)
async def get_latest_price(
    session: SessionDep,
    ticker: str = Query(..., description="Currency ticker: btc_usd or eth_usd"),
) -> PriceRead:
    """
    Get the latest price for a specified currency ticker.

    Returns the most recent price record for the given cryptocurrency.
    Useful for getting current market price or real-time tracking.

    Args:
        session: Database session dependency
        ticker: Currency ticker symbol. Must be either 'btc_usd' or 'eth_usd'

    Returns:
        PriceRead: The latest price record for the specified ticker

    Raises:
        HTTPException:
            400 - If ticker is not 'btc_usd' or 'eth_usd'
            404 - If no prices found for the specified ticker
    """
    if ticker not in ["btc_usd", "eth_usd"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid ticker. Allowed values: btc_usd, eth_usd",
        )

    service = DeribitService(session=session)
    latest_price = await service.get_last_known_price(ticker=ticker)

    if not latest_price:
        raise HTTPException(
            status_code=404, detail=f"No prices found for ticker '{ticker}'"
        )

    return PriceRead.model_validate(latest_price)


@router.get("/filter", response_model=PriceList)
async def get_prices_by_date(
    session: SessionDep,
    ticker: str = Query(..., description="Currency ticker: btc_usd or eth_usd"),
    start_date: str | None = Query(
        None, description="Start date in format: YYYY-MM-DD"
    ),
    end_date: str | None = Query(None, description="End date in format: YYYY-MM-DD"),
) -> PriceList:
    """
    Get price records filtered by date range.

    Returns price data for a specified ticker within the given date range.
    Supports filtering by start date, end date, or both. If no dates are provided,
    returns all records (same as the root endpoint).

    Args:
        session: Database session dependency
        ticker: Currency ticker symbol. Must be either 'btc_usd' or 'eth_usd'
        start_date: Start date (inclusive) in ISO format: YYYY-MM-DD
        end_date: End date (inclusive) in ISO format: YYYY-MM-DD

    Returns:
        PriceList: List of price records within the specified date range

    Raises:
        HTTPException:
            400 - If ticker is invalid or date format is incorrect
    """
    if ticker not in ["btc_usd", "eth_usd"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid ticker. Allowed values: btc_usd, eth_usd",
        )

    start_ts = None
    end_ts = None

    if start_date:
        try:
            dt = datetime.strptime(start_date, "%Y-%m-%d")
            start_ts = int(dt.timestamp() * 1_000_000)
        except ValueError as err:
            raise HTTPException(
                status_code=400,
                detail="Invalid start_date format. Use: YYYY-MM-DD",
            ) from err

    if end_date:
        try:
            dt = datetime.strptime(end_date, "%Y-%m-%d")
            end_of_day = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            end_ts = int(end_of_day.timestamp() * 1_000_000)
        except ValueError as err:
            raise HTTPException(
                status_code=400,
                detail="Invalid end_date format. Use: YYYY-MM-DD",
            ) from err

    service = DeribitService(session=session)
    currency_prices = await service.get_prices_with_by_date(
        ticker=ticker, start_ts=start_ts, end_ts=end_ts
    )

    items = [PriceRead.model_validate(price) for price in currency_prices]
    return PriceList(items=items)
