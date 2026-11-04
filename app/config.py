from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./recommendation.db"
    app_env: str = "development"
    log_level: str = "INFO"
    interaction_weights: dict[str, float] = {"view": 1, "virtual_try_on": 3, "mix_and_match": 4, "add_to_cart": 5, "purchase": 10}
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

