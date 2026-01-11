import json
import logging
from typing import Any, AsyncIterator

from aiokafka import AIOKafkaConsumer
from aiokafka.structs import TopicPartition

from src.config import KafkaConsumerConfig

logger = logging.getLogger(__name__)


class KafkaConsumer:
    def __init__(self, cfg: KafkaConsumerConfig, *, topic: str) -> None:
        self._cfg = cfg
        self._topic = topic
        self._consumer: AIOKafkaConsumer | None = None

    async def start(self) -> None:
        if self._consumer is not None:
            return
        self._consumer = AIOKafkaConsumer(
            self._topic,
            bootstrap_servers=self._cfg.bootstrap_servers,
            group_id=self._cfg.group_id,
            auto_offset_reset=self._cfg.auto_offset_reset,
            enable_auto_commit=self._cfg.enable_auto_commit,
        )
        await self._consumer.start()
        logger.info("consumer запущен")

    async def seek_to_end(self) -> None:
        if self._consumer is None:
            raise RuntimeError("consumer не запущен")

        await self._consumer.getmany(timeout_ms=0)

        parts = self._consumer.assignment()
        if not parts:
            partitions = await self._consumer.partitions_for_topic(self._topic)
            if partitions:
                tps = {TopicPartition(self._topic, p) for p in partitions}
                self._consumer.assign(tps)
                parts = tps

        if parts:
            await self._consumer.seek_to_end(*parts)

    async def stop(self) -> None:
        if self._consumer is None:
            return
        await self._consumer.stop()
        self._consumer = None

    async def __aiter__(self) -> AsyncIterator[dict[str, Any]]:
        if self._consumer is None:
            raise RuntimeError("consumer не запущен")

        async for message in self._consumer:
            logger.info(f"Получено сообщение {message}")
            yield json.loads(message.value.decode("utf-8"))

async def consume_model_responses(app_state) -> None:
    async for data in app_state.kafka_consumer:
        user_id = data.get("user_id")
        message_id = data.get("message_id")
        answer = data.get("answer")

        if user_id is None or message_id is None:
            continue

        key = (int(user_id), int(message_id))

        async with app_state.pending_lock:
            fut = app_state.pending.pop(key, None)

        if fut and not fut.done():
            fut.set_result(answer or "Пустой ответ от модели")
