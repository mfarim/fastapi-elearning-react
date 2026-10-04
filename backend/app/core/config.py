import os
from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )

    APP_NAME: str = "Python FastAPI E-Learning LMS & CBT"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000

    # PostgreSQL Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5434/elearning"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://postgres:postgres@localhost:5434/elearning"

    # Redis
    REDIS_URL: str = "redis://localhost:6380/0"

    # Security & JWT
    SECRET_KEY: str = "404E635266556A586E3272357538782F413F4428472B4B6250645367566B5970"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Storage
    STORAGE_DRIVER: str = "local"
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "storage/uploads")
    MAX_FILE_SIZE_MB: int = 50

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9002"
    MINIO_ROOT_USER: str = "minioadmin"
    MINIO_ROOT_PASSWORD: str = "minioadmin"
    MINIO_BUCKET: str = "elearning-media"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
    ]


settings = Settings()
