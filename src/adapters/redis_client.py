from redis.asyncio import Redis

from src.config import config


def get_redis() -> Redis:
    return Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)
