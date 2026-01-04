import asyncio

import httpx
from celery.utils.log import get_task_logger

from src.adapters.celery_app import celery_app
from src.adapters.redis_client import get_redis
from src.dto import ModelSyncResult
from src.services.model_catalog import ModelCatalogService
from src.services.model_registry import ModelRegistry

logger = get_task_logger(__name__)


async def _sync_models_async() -> ModelSyncResult:
    redis = get_redis()
    registry = ModelRegistry(redis)
    catalog = ModelCatalogService()

    try:
        models = await catalog.fetch_models()
    except httpx.HTTPError as exc:
        logger.error(
            "Не удалось получить список моделей от оркестратора",
            exc_info=exc,
        )
        return ModelSyncResult.error(reason="http_error")

    await registry.replace_models(models)

    logger.info(f"Кеш доступных моделей обновлён. Модели {models}")

    return ModelSyncResult.ok(count=len(models))


@celery_app.task(name="src.tasks.sync_models_task")
def sync_models_task():
    result = asyncio.run(_sync_models_async())
    return result.__dict__
