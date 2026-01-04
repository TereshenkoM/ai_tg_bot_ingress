from redis.asyncio import Redis

from src.config import config


class ModelRegistry:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.models_key = config.AVAILABLE_MODELS_KEY
        self.version_key = config.AVAILABLE_MODELS_VERSION_KEY
        self.mock = config.MOCK

    async def list_models(self) -> list[str]:
        if self.mock:
            return config.DEFAULT_MODELS

        models = await self.redis.smembers(self.models_key)
        return sorted(
            model.decode() if isinstance(model, (bytes, bytearray)) else str(model)
            for model in models
        )

    async def replace_models(self, models: list[str]) -> None:
        pipe = self.redis.pipeline(transaction=True)
        await pipe.delete(self.models_key)

        if models:
            await pipe.sadd(self.models_key, *models)

        time = await self.redis.time()
        await pipe.set(self.version_key, str(int(time[0])))
        await pipe.execute()
