from pathlib import Path

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
ENV_TEMPLATE_PATH = PROJECT_ROOT / ".env.template"


class DatabaseConfig(BaseModel):
    """
    Database connection and pooling configuration.

    This configuration class defines all PostgreSQL database connection
    parameters, connection pool settings, and SQLAlchemy naming conventions.
    """

    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class RunConfig(BaseModel):
    """
    Application runtime server configuration.

    Defines parameters for the ASGI server (Uvicorn) that runs the FastAPI application.
    """

    host: str = "0.0.0.0"
    port: int = 8000


class ApiV1Prefix(BaseModel):
    """
    API version 1 URL path prefixes.

    Defines the URL structure for API version 1 endpoints to maintain
    consistent and versioned API routes.
    """

    prefix: str = "/v1"
    deribit: str = "/deribit"


class ApiPrefix(BaseModel):
    """
    Root API URL path configuration.

    Defines the base URL structure for the entire API, including
    versioning and resource grouping.
    """

    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class Settings(BaseSettings):
    """
    Main application configuration settings.

    This is the root configuration class that loads and validates all
    application settings from environment variables using Pydantic Settings.

    Configuration Strategy:
        - Environment-based configuration (12-factor app)
        - Nested configuration structure for organization
        - Sensible defaults with environment overrides
        - Strong typing and validation with Pydantic
    """

    model_config = SettingsConfigDict(
        env_file=(ENV_TEMPLATE_PATH, ENV_PATH),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig


settings = Settings()
