from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class BasePrice(BaseModel):
    """
    Base schema for cryptocurrency price data.
    """

    ticker: str
    price: Decimal
    timestamp: int


class PriceRead(BasePrice):
    """
    Read-only schema for price data retrieved from the database.
    """

    id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class PriceList(BaseModel):
    """
    Container schema for lists of price records.
    """

    items: list[PriceRead]
