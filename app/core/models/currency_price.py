from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String, func, BigInteger, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models.base import Base


class CurrencyPrice(Base):
    ticker: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )
    price: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    timestamp: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"Currency(id={self.id}, ticker={self.ticker}, price={self.price})"
