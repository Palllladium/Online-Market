from pydantic import BaseModel
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class JWTSettings(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7


class Settings(BaseSettings):
    # --- Auth Postgres ---
    AUTH_POSTGRES_DB: str
    AUTH_POSTGRES_USER: str
    AUTH_POSTGRES_PASSWORD: str
    AUTH_POSTGRES_HOST: str
    AUTH_POSTGRES_PORT: int

    # --- Products Postgres ---
    PRODUCTS_POSTGRES_DB: str
    PRODUCTS_POSTGRES_USER: str
    PRODUCTS_POSTGRES_PASSWORD: str
    PRODUCTS_POSTGRES_HOST: str
    PRODUCTS_POSTGRES_PORT: int

    # --- Redis ---
    REDIS_HOST: str
    REDIS_PORT: int

    # --- Auth service ---
    AUTH_SERVICE_HOST: str
    AUTH_SERVICE_PORT: int
    AUTH_SERVICE_PATH: str

    # --- Elasticsearch & Search service ---
    ELASTICSEARCH_HOST: str
    ELASTICSEARCH_PORT: int
    ELASTICSEARCH_INDEX_NAME: str
    ELASTICSEARCH_SEARCH_SIZE: int

    SEARCH_SERVICE_HOST: str
    SEARCH_SERVICE_PORT: int
    SEARCH_SERVICE_PATH: str

    # --- Schedulers etc ---
    SCHEDULE_INTERVAL_SECONDS: int

    # --- JWT ---
    JWT: JWTSettings = JWTSettings()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def auth_postgres_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.AUTH_POSTGRES_USER}:{self.AUTH_POSTGRES_PASSWORD}@"
            f"{self.AUTH_POSTGRES_HOST}:{self.AUTH_POSTGRES_PORT}/"
            f"{self.AUTH_POSTGRES_DB}"
        )

    @property
    def products_postgres_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.PRODUCTS_POSTGRES_USER}:{self.PRODUCTS_POSTGRES_PASSWORD}@"
            f"{self.PRODUCTS_POSTGRES_HOST}:{self.PRODUCTS_POSTGRES_PORT}/"
            f"{self.PRODUCTS_POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def elastic_search_url(self) -> str:
        return f"http://{self.ELASTICSEARCH_HOST}:{self.ELASTICSEARCH_PORT}"

    @property
    def search_service_url(self) -> str:
        return f"http://{self.SEARCH_SERVICE_HOST}:{self.SEARCH_SERVICE_PORT}{self.SEARCH_SERVICE_PATH}"
    
    @property
    def auth_service_url(self) -> str:
        return f"http://{self.AUTH_SERVICE_HOST}:{self.AUTH_SERVICE_PORT}{self.AUTH_SERVICE_PATH}"


@lru_cache()
def get_settings() -> Settings:
    return Settings()