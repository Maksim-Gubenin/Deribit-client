import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.currency_price import CurrencyPrice
from app.repositories.deribit_repository import DeribitRepository


@pytest.mark.asyncio
async def test_add_price(test_session: AsyncSession) -> None:
    """
    Test adding a new price record to the database.

    Verifies that the price is correctly saved and all fields (ticker, price, timestamp)
    match the input data.

    Args:
        test_session (AsyncSession): The asynchronous database session.
    """
    repo: DeribitRepository = DeribitRepository(test_session)

    await repo.add_price("btc_usd", 50000.50, 1640995200123456)

    prices = await repo.get_all_by_ticker("btc_usd")
    assert len(prices) == 1
    assert prices[0].ticker == "btc_usd"
    assert float(prices[0].price) == 50000.50
    assert prices[0].timestamp == 1640995200123456


@pytest.mark.asyncio
async def test_get_all_by_ticker(test_session: AsyncSession) -> None:
    """
    Test retrieving all price records for a specific ticker.

    Ensures that the repository filters records correctly by ticker and
    does not return data belonging to other assets.

    Args:
        test_session (AsyncSession): The asynchronous database session.
    """
    repo: DeribitRepository = DeribitRepository(test_session)

    await repo.add_price("btc_usd", 50000.50, 1640995200123456)
    await repo.add_price("btc_usd", 50100.75, 1640995260123456)
    await repo.add_price("eth_usd", 3000.25, 1640995200123456)

    btc_prices: list[CurrencyPrice] = await repo.get_all_by_ticker("btc_usd")
    assert len(btc_prices) == 2
    assert all(p.ticker == "btc_usd" for p in btc_prices)

    eth_prices = await repo.get_all_by_ticker("eth_usd")
    assert len(eth_prices) == 1
    assert eth_prices[0].ticker == "eth_usd"


@pytest.mark.asyncio
async def test_get_latest(test_session: AsyncSession) -> None:
    """
    Test retrieving the most recent price record for a ticker.

    Verifies that the repository returns the record with the highest timestamp.

    Args:
        test_session (AsyncSession): The asynchronous database session.
    """
    repo: DeribitRepository = DeribitRepository(test_session)

    await repo.add_price("btc_usd", 50000.50, 1640995200123456)  # Old
    await repo.add_price("btc_usd", 50100.75, 1640995260123456)  # New

    latest: CurrencyPrice | None = await repo.get_latest("btc_usd")

    assert latest is not None
    assert float(latest.price) == 50100.75


@pytest.mark.asyncio
async def test_get_latest_empty(test_session: AsyncSession) -> None:
    """
    Test the behavior of get_latest when no data is available.

    Args:
        test_session (AsyncSession): The asynchronous database session.
    """
    repo: DeribitRepository = DeribitRepository(test_session)
    latest: CurrencyPrice | None = await repo.get_latest("btc_usd")
    assert latest is None


@pytest.mark.asyncio
async def test_get_by_range(test_session: AsyncSession) -> None:
    """
    Test retrieving price records within a specific timestamp range.

    Args:
        test_session (AsyncSession): The asynchronous database session.
    """
    repo: DeribitRepository = DeribitRepository(test_session)

    timestamps: list[int] = [
        1640995200123456,
        1641081600123456,
        1641168000123456,
    ]

    for i, ts in enumerate(timestamps):
        await repo.add_price("btc_usd", 50000.50 + i * 100, ts)

    prices = await repo.get_by_range(
        ticker="btc_usd", start_ts=1641081600123456, end_ts=1641168000123456
    )

    assert len(prices) == 2
    assert prices[0].timestamp == 1641081600123456
    assert prices[1].timestamp == 1641168000123456
