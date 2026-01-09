import asyncio

from logger import setup_logging, get_logger

from aiogram import Bot, Dispatcher

from src.adapters.kafka_producer import KafkaProducer, KafkaProducerConfig
from src.adapters.redis_client import get_redis
from src.config import config
from src.dto import AppState
from src.router_registry import setup_routers
from src.services.model_registry import ModelRegistry

setup_logging(service_name="ingress")
logger = get_logger(__name__)

async def main() -> None:
    bot = Bot(token=config.TG_BOT_TOKEN)
    dp = Dispatcher()

    redis = get_redis()
    kafka = KafkaProducer(
        KafkaProducerConfig(bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS)
    )
    model_registry = ModelRegistry(redis)

    app_state = AppState(redis=redis, kafka=kafka, model_registry=model_registry)
    dp.workflow_data["app_state"] = app_state

    dp.workflow_data["app_state"] = app_state

    dp.include_router(setup_routers())

    await kafka.start()
    try:
        await dp.start_polling(bot)
    finally:
        await kafka.stop()
        await redis.aclose()


if __name__ == "__main__":
    asyncio.run(main())
