from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class BasePrice(BaseModel):
    ticker: str
    price: Decimal
    timestamp: int


class PriceRead(BasePrice):
    id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class PriceList(BaseModel):
    items: list[PriceRead]
