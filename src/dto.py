import asyncio
from dataclasses import dataclass
from typing import Optional

from redis.asyncio import Redis

from src.adapters.kafka_consumer import KafkaConsumer
from src.adapters.kafka_producer import KafkaProducer
from src.services.model_registry import ModelRegistry


@dataclass(slots=True)
class AppState:
    redis: Redis
    kafka_producer: KafkaProducer
    kafka_consumer: KafkaConsumer
    model_registry: ModelRegistry
    pending: dict[tuple[int, int], asyncio.Future[str]]
    pending_lock: asyncio.Lock


@dataclass(slots=True)
class ModelSyncResult:
    status: str
    count: int = 0
    reason: Optional[str] = None

    @classmethod
    def ok(cls, count: int) -> "ModelSyncResult":
        return cls(status="ok", count=count)

    @classmethod
    def error(cls, reason: str) -> "ModelSyncResult":
        return cls(status="error", reason=reason)
