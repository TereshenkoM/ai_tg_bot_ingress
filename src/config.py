from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    TG_BOT_TOKEN: str
    REDIS_HOST: str
    REDIS_PORT: int
    MOCK: bool
    USER_MODEL_KEY_PATTERN: str
    AVAILABLE_MODELS_KEY: str
    AVAILABLE_MODELS_VERSION_KEY: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    MODEL_SYNC_INTERVAL_SEC: int
    MANAGEMENT_SERVICE_URL: str
    MANAGEMENT_SERVICE_MODEL_ENDPOINT: str

    DEFAULT_MODELS: list[str] = ["gemini", "chatgpt"]

    model_config = SettingsConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"
    )


config = Config()
