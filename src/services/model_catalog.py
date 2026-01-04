import asyncio
import random
from itertools import count, islice

import httpx

from src.config import config


class ModelCatalogService:
    def __init__(
        self,
        management_service_url: str | None = None,
        management_service_models_endpoint: str | None = None,
        *,
        max_attempts: int = 5,
        base_delay: float = 0.5,
        max_delay: float = 5.0,
        jitter: float = 0.2,
    ) -> None:
        self.management_service_url = (
            management_service_url if management_service_url else config.MANAGEMENT_SERVICE_URL
        )
        self.management_service_models_endpoint = (
            management_service_models_endpoint
            if management_service_models_endpoint
            else config.MANAGEMENT_SERVICE_MODEL_ENDPOINT
        )

        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter

    async def fetch_models(self) -> list[str]:
        models_url = f"{self.management_service_url}{self.management_service_models_endpoint}"

        timeout = httpx.Timeout(5.0, connect=2.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await self._get_with_retries(client, models_url)
            data = response.json()

        models = data.get("models", [])
        return [model.strip() for model in models if isinstance(model, str) and model.strip()]

    async def _get_with_retries(self, client: httpx.AsyncClient, url: str) -> httpx.response:
        last_exc: Exception | None = None

        for attempt, delay in self._attempts_with_delays():
            try:
                response = await client.get(url)

                if 200 <= response.status_code < 300:
                    return response

                if response.status_code in (429, 500, 502, 503, 504):
                    await asyncio.sleep(delay)
                    continue

                response.raise_for_status()
                return response

            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_exc = exc
                await asyncio.sleep(delay)
                continue

        if last_exc:
            raise last_exc
        raise RuntimeError("Не удалось получить список моделей: исчерпаны попытки")

    def _attempts_with_delays(self):
        for attempt in islice(count(1), self.max_attempts):
            delay = min(self.base_delay * (2 ** (attempt - 1)), self.max_delay)

            if self.jitter > 0:
                spread = delay * self.jitter
                delay += random.uniform(-spread, spread)
            yield attempt, max(0.0, delay)
