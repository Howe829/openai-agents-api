# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    LLM_BASE_URL: str
    LLM_API_KEY: str
    LLM_MODEL: str
    TIMEZONE: str = "Asia/Shanghai"


settings = Settings()
