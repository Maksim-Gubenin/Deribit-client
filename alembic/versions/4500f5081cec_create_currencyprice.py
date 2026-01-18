"""Create CurrencyPrice

Revision ID: 4500f5081cec
Revises:
Create Date: 2026-01-18 09:09:13.601238

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4500f5081cec"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "currency_prices",
        sa.Column("ticker", sa.String(length=10), nullable=False),
        sa.Column("price", sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column("timestamp", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_currency_prices")),
    )
    op.create_index(
        op.f("ix_currency_prices_ticker"),
        "currency_prices",
        ["ticker"],
        unique=False,
    )
    op.create_index(
        op.f("ix_currency_prices_timestamp"),
        "currency_prices",
        ["timestamp"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_currency_prices_timestamp"), table_name="currency_prices")
    op.drop_index(op.f("ix_currency_prices_ticker"), table_name="currency_prices")
    op.drop_table("currency_prices")
