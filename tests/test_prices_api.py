from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.currency_price import CurrencyPrice


@pytest.mark.asyncio
async def test_get_all_prices_success(
    client: TestClient, test_session: AsyncSession
) -> None:
    """
    Integration test for retrieving all historical prices for a specific ticker.

    This test seeds the database with a single price record, performs a GET request
    via the TestClient, and verifies that the returned data matches the seeded record.

    Args:
        client (TestClient): The HTTP test client configured with the API base URL.
        test_session (AsyncSession): The database session used to seed test data.

    Returns:
        None
    """
    price1: CurrencyPrice = CurrencyPrice(
        ticker="btc_usd",
        price=50000.5,
        timestamp=1640995200,
        created_at=datetime.now(UTC),
    )
    test_session.add(price1)
    await test_session.commit()

    response = client.get("/?ticker=btc_usd")

    assert response.status_code == 200

    data: dict[str, Any] = response.json()
    assert len(data["items"]) == 1
    assert float(data["items"][0]["price"]) == 50000.5


@pytest.mark.asyncio
async def test_get_latest_price_not_found(client: TestClient) -> None:
    """
    Integration test for the latest price endpoint when no data is found.

    Verifies that the API correctly returns a 404 Not Found status code
    when a request is made for a ticker that has no records in the database.

    Args:
        client (TestClient): The HTTP test client configured with the API base URL.

    Returns:
        None
    """
    response = client.get("/latest?ticker=eth_usd")

    assert response.status_code == 404
