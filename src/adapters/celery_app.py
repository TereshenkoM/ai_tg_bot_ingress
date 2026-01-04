from celery import Celery

from src.config import config

celery_app = Celery(
    "bot_model_sync",
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
)
celery_app.autodiscover_tasks(["src"])
celery_app.conf.timezone = "Europe/Moscow"

celery_app.conf.broker_transport_options = {
    "visibility_timeout": 3600,
    "socket_timeout": 5,
    "socket_connect_timeout": 5,
}
celery_app.conf.redis_backend_transport_options = {
    "socket_timeout": 5,
    "socket_connect_timeout": 5,
}

if not config.MOCK:
    celery_app.conf.beat_schedule = {
        "sync-models": {
            "task": "src.tasks.sync_models_task",
            "schedule": float(config.MODEL_SYNC_INTERVAL_SEC),
        }
    }