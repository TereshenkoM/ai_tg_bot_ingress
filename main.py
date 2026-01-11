import asyncio

from aiogram import Bot, Dispatcher
from logger import get_logger, setup_logging

from src.adapters.kafka_consumer import KafkaConsumer
from src.adapters.kafka_producer import KafkaProducer
from src.adapters.redis_client import get_redis
from src.config import KafkaConsumerConfig, KafkaProducerConfig, config
from src.dto import AppState
from src.router_registry import setup_routers
from src.services.model_registry import ModelRegistry

setup_logging(service_name="ingress")
logger = get_logger(__name__)


async def main() -> None:
    bot = Bot(token=config.TG_BOT_TOKEN)
    dp = Dispatcher()

    redis = get_redis()
    kafka_producer = KafkaProducer(
        KafkaProducerConfig(bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS)
    )
    kafka_consumer = KafkaConsumer(
        KafkaConsumerConfig(
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
            group_id=config.KAFKA_GROUP_ID,
            enable_auto_commit=True,
        ),
        topic=config.TOPIC_MODEL_RESPONSES,
    )
    model_registry = ModelRegistry(redis)

    pending = {}
    pending_lock = asyncio.Lock()

    app_state = AppState(
        redis=redis,
        kafka_producer=kafka_producer,
        model_registry=model_registry,
        kafka_consumer=kafka_consumer,
        pending=pending,
        pending_lock=pending_lock,
    )
    dp.workflow_data["app_state"] = app_state

    dp.workflow_data["app_state"] = app_state

    dp.include_router(setup_routers())

    await kafka_producer.start()
    await kafka_consumer.start()

    try:
        await kafka_consumer.seek_to_end()
        await dp.start_polling(bot)
    finally:
        await kafka_producer.stop()
        await kafka_consumer.stop()
        await redis.aclose()


if __name__ == "__main__":
    asyncio.run(main())
