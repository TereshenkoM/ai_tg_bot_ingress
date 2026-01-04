from redis.asyncio import Redis

from src.config import config


class UserModelService:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get_selected_model(self, user_id: int) -> str | None:
        key = config.USER_MODEL_KEY_PATTERN.format(user_id=user_id)
        value = await self.redis.get(key)
        if value is None:
            return None
        return value.decode() if isinstance(value, (bytes, bytearray)) else str(value)
