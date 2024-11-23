import os

from dotenv import load_dotenv
from typing import Sequence
from pydantic_settings import BaseSettings
from urllib.parse import quote
from pydantic import DirectoryPath

load_dotenv()


class DBConfig(BaseSettings):
    DB_NAME: str = os.getenv("DB_NAME", "api")
    DB_USER: str = os.getenv("DB_USER", "admin")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")

    SQLALCHEMY_DATABASE_URL: str = f"postgresql+asyncpg://{DB_USER}:{quote(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


class Config(BaseSettings):
    APP_VERSION: str = "1.0"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "ChangeMe")
    JWT_REFRESH_SECRET_KEY: str = os.getenv("JWT_REFRESH_SECRET_KEY", "ChangeMe")

    CORS_ORIGINS: Sequence[str] = ["*"]
    CORS_ORIGINS_REGEX: str | None = None
    CORS_HEADERS: Sequence[str] = [""]

    BASE_DIR: DirectoryPath = os.path.dirname(
        os.path.dirname(os.path.realpath(__file__))
    )

    STATIC_DIR: str = "/static"

    LOGGING_CONFIG: object = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "level": "INFO",
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "level": "INFO",
                "formatter": "default",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": BASE_DIR + "/app.log",
                "maxBytes": 1024 * 1024 * 10,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            "": {  # Root logger
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "DEBUG",
                "handlers": ["file"],
            },
            "uvicorn.access": {
                "level": "DEBUG",
                "handlers": ["file"],
            },
        },
    }


settings = Config()
db_settings = DBConfig()
