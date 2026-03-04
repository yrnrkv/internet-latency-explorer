from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://latency:latency@localhost:5432/latency"
    redis_url: str = "redis://localhost:6379"
    api_keys: list[str] = ["dev-api-key"]
    allowed_origins: list[str] = ["*"]
    rate_limit_per_minute: int = 60

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
