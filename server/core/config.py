from pydantic_settings import BaseSettings
from pathlib import Path

ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    database_url: str
    secret_key: str = "change-me-in-production-use-openssl-rand-hex-32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    class Config:
        env_file = str(ENV_FILE)


settings = Settings()
