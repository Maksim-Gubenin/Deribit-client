"""
Base SQLAlchemy declarative base class with automatic table naming.

This module provides a custom base class for SQLAlchemy models that automatically
generates table names from class names using camelCase to snake_case conversion,
and includes a standard primary key field.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)

from app.core.config import settings
from app.utils import camel_case_to_snake_case


class Base(DeclarativeBase):
    """
    Custom SQLAlchemy declarative base class with automatic table naming.

    This class extends SQLAlchemy's DeclarativeBase to provide:
    1. Automatic table name generation from class names
    2. Standard primary key field (id)
    3. Consistent naming conventions across all models

    Attributes:
        id (Mapped[int]): Primary key field automatically added to all models.

    Example:
        class User(Base):
        ...name: Mapped[str]
        ...email: Mapped[str]
        User.__tablename__
        'users'  # Automatically generated from 'User' + 's'
        User.__table__.primary_key.columns
        ['id']  # Automatically included primary key

    """

    __abstract__ = True

    metadata = MetaData(
        naming_convention=settings.db.naming_convention,
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Automatically generate table name from class name.

        This class method is called by SQLAlchemy when creating tables to
        determine the table name. It converts the PascalCase class name to
        snake_case and pluralizes it by adding 's'.

        Args:
            cls: The model class being defined.

        Returns:
            Table name in snake_case plural form.

        Transformation Rules:
            Class Name → Table Name
            ----------   ----------
            User        → users
            ProductItem → product_items
            Order       → orders
        """
        # Единые правила по именованию таблиц
        return f"{camel_case_to_snake_case(cls.__name__)}s"

    id: Mapped[int] = mapped_column(primary_key=True)
