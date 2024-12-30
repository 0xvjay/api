import os
from typing import Sequence
from urllib.parse import quote

from dotenv import load_dotenv
from pydantic import DirectoryPath
from pydantic_settings import BaseSettings

load_dotenv()


class DBConfig(BaseSettings):
    DB_NAME: str = os.getenv("DB_NAME", "api")
    TEST_DB_NAME: str = os.getenv("TEST_DB_NAME", "api")
    DB_USER: str = os.getenv("DB_USER", "admin")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")

    SQLALCHEMY_DATABASE_URL: str = f"postgresql+asyncpg://{DB_USER}:{quote(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TEST_DATABASE_URL: str = f"postgresql+asyncpg://{DB_USER}:{quote(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}"


class Config(BaseSettings):
    APP_VERSION: str = "1.0"

    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "ChangeMe")
    JWT_REFRESH_SECRET_KEY: str = os.getenv("JWT_REFRESH_SECRET_KEY", "ChangeMe")

    CORS_ORIGINS: Sequence[str] = ["*"]
    CORS_ORIGINS_REGEX: str | None = None
    CORS_HEADERS: Sequence[str] = [""]

    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")
    MAIL_FROM: str = os.getenv("MAIL_FROM")
    MAIL_SERVER: str = os.getenv("MAIL_SERVER")
    MAIL_PORT: int = 587

    BASE_DIR: DirectoryPath = os.path.dirname(
        os.path.dirname(os.path.realpath(__file__))
    )

    STATIC_DIR: str = "static"

    LOGGING_CONFIG: object = {
        "version": 1,
        "disable_existing_loggers": False,
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
