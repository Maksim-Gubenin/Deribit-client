from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.currency_price import CurrencyPrice
from app.services.deribit_service import DeribitService


@pytest.mark.asyncio
async def test_collect_and_save_prices(test_session: AsyncSession) -> None:
    """
    Test collecting and saving price data through the service layer.

    Mocks the Deribit API client to simulate fetching index data and verifies
    that the service correctly persists this data to the database.

    Args:
        test_session (AsyncSession): The asynchronous database session.
    """
    mock_client: Mock = Mock()
    mock_client.get_index_data = AsyncMock(
        return_value={"result": {"index_price": 50000.50}, "usIn": 1640995200123456}
    )

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.services.deribit_service.DeribitClient", lambda: mock_client)
        service: DeribitService = DeribitService(test_session)

        await service.collect_and_save_prices("btc_usd")

        mock_client.get_index_data.assert_called_once_with(ticker="btc_usd")

        prices = await service.get_prices_by_all_date("btc_usd")
        assert len(prices) == 1
        assert prices[0].ticker == "btc_usd"
        assert float(prices[0].price) == 50000.50


@pytest.mark.asyncio
async def test_get_prices_by_all_date(test_session: AsyncSession) -> None:
    """
    Test retrieving all stored prices for a specific ticker via the service.

    Args:
        test_session (AsyncSession): The asynchronous database session.
    """
    service: DeribitService = DeribitService(test_session)

    await service.repo.add_price("btc_usd", 50000.50, 1640995200123456)
    await service.repo.add_price("btc_usd", 50100.75, 1640995260123456)

    prices = await service.get_prices_by_all_date("btc_usd")

    assert len(prices) == 2
    assert all(p.ticker == "btc_usd" for p in prices)


@pytest.mark.asyncio
async def test_get_last_known_price(test_session: AsyncSession) -> None:
    """
    Test retrieving the most recent price record for a ticker.

    Args:
        test_session (AsyncSession): The asynchronous database session.
    """
    service: DeribitService = DeribitService(test_session)

    await service.repo.add_price("btc_usd", 50000.50, 1640995200123456)
    await service.repo.add_price("btc_usd", 50100.75, 1640995260123456)

    latest: CurrencyPrice | None = await service.get_last_known_price("btc_usd")

    assert latest is not None
    assert float(latest.price) == 50100.75


@pytest.mark.asyncio
async def test_get_last_known_price_empty(test_session: AsyncSession) -> None:
    """
    Test retrieving the last known price when the database is empty.

    Args:
        test_session (AsyncSession): The asynchronous database session.
    """
    service: DeribitService = DeribitService(test_session)

    latest: CurrencyPrice | None = await service.get_last_known_price("btc_usd")

    assert latest is None
