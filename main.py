import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher

from src.adapters.redis_client import get_redis
from src.config import config
from src.router_registry import setup_router
from src.services.model_registry import ModelRegistry


async def main():
    if not config.TG_BOT_TOKEN:
        raise RuntimeError("TG_BOT_TOKEN is empty")

    bot = Bot(token=config.TG_BOT_TOKEN)
    dp = Dispatcher()

    redis = get_redis()
    registry = ModelRegistry(redis)

    dp.workflow_data["redis"] = redis
    dp.workflow_data["model_registry"] = registry

    dp.include_router(setup_router())
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
