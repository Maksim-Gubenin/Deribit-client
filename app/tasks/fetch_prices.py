import asyncio
import logging

from celery import shared_task

from app.core.config import settings
from app.core.db_helper import DatabaseHelper
from app.services.deribit_service import DeribitService

logger = logging.getLogger(__name__)


async def fetch_prices_internal() -> None:
    """
    Internal async function to fetch and save cryptocurrency prices from Deribit.

    This function creates an isolated database connection for each execution,
    fetches BTC/USD and ETH/USD index prices from Deribit API, and saves them
    to the PostgreSQL database. Each ticker is processed independently to ensure
    that an error with one currency doesn't affect the other.

    Architecture Notes:
        - Creates a new DatabaseHelper instance for complete isolation
        - Uses a small connection pool (size=1) as each task runs independently
        - Each ticker is processed in a separate try-catch block
        - Database connection is properly disposed after execution

    Error Handling:
        - Logs errors for individual tickers but continues processing
        - Database connection is always disposed even if errors occur

    Returns:
        None: This function performs side effects (saves to database)

    Raises:
        Exception: Any exception from aiohttp, SQLAlchemy, or database operations
    """
    local_db = DatabaseHelper(
        url=str(settings.db.url),
        echo=False,
        echo_pool=False,
        pool_size=1,
        max_overflow=0,
    )

    try:
        async with local_db.session_factory() as session:
            service = DeribitService(session=session)

            for ticker in ["btc_usd", "eth_usd"]:
                try:
                    await service.collect_and_save_prices(ticker=ticker)
                    logger.info(f"✅ {ticker} saved")
                except Exception as e:
                    logger.error(f"❌ {ticker} error: {e}")
    finally:
        await local_db.dispose()


@shared_task
def fetch_prices_task() -> None:
    """
    Celery scheduled task to periodically fetch cryptocurrency prices.

    This is the main entry point for the Celery beat scheduler. It runs
    every 60 seconds (as configured in celery_config.py) to fetch current
    BTC/USD and ETH/USD index prices from Deribit and store them in the database.

    Key Features:
        - Scheduled execution via Celery Beat
        - Creates a new event loop for async execution
        - Proper error handling and logging
        - Isolated database connections per execution

    Task Configuration:
        - Schedule: 60 seconds (configurable in celery_config.py)
        - Max retries: Configured in Celery worker settings
        - Timeout: Default Celery task timeout

    Monitoring:
        - Success: Logs "✅ Task cycle completed"
        - Errors: Logged at error level with full traceback
        - Individual currency errors: Logged separately

    Example Celery Command:
        ```bash
        # Start Celery worker with beat scheduler
        celery -A app.core.celery_config.celery_app worker --beat --loglevel=info

        # Monitor scheduled tasks
        celery -A app.core.celery_config.celery_app inspect scheduled
        ```

    Returns:
        None: Celery task result is not stored (ignore_result=True by default)

    Raises:
        Exception: Any unhandled exception will be logged by Celery and may
                   trigger retries based on Celery configuration
    """
    asyncio.run(fetch_prices_internal())

    logger.info("✅ Task cycle completed")
