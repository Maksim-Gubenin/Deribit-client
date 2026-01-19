from celery import Celery

celery_app = Celery(
    "deribit_tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["app.tasks.fetch_prices"],
)

celery_app.conf.beat_schedule = {
    "fetch-prices": {
        "task": "app.tasks.fetch_prices.fetch_prices_task",
        "schedule": 60.0,
    },
}
