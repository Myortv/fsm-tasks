from typing import Optional

import logging
import logging.config


from pydantic_settings import BaseSettings, SettingsConfigDict


logging.config.fileConfig("src/core/log.config")
logging.basicConfig(level=logging.INFO)
# logging.getLogger().setLevel(logging.DEBUG)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    BOT_NAME: str = "cool bot"

    PYROGRAM_API_ID: str
    PYROGRAM_API_HASH: str
    PYROGRAM_BOT_TOKEN: str

    POSTGRES_DB: Optional[str] = 'postgres'
    POSTGRES_USER: Optional[str] = 'postgres'
    POSTGRES_HOST: Optional[str] = 'postgres'
    POSTGRES_PASSWORD: Optional[str] = 'postgres'

    DEBUG: Optional[bool] = False


settings = Settings()
# settings.DEBUG = True
