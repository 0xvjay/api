import logging.config
import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.auth.router import router as auth_router
from api.catalogue.router import router as catalogue_router
from api.config import settings
from api.order.router import router as order_router
from api.user.router import router as user_router

logging.config.dictConfig(settings.LOGGING_CONFIG)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)


if settings.STATIC_DIR and os.path.isdir(settings.STATIC_DIR):
    app.mount("/", StaticFiles(directory=settings.STATIC_DIR), name="static")


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(catalogue_router)
app.include_router(order_router)

if __name__ == "__main__":
    uvicorn_config = {
        "app": "main:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True,
    }
    import sys

    if sys.platform != "win32":
        uvicorn_config["loop"] = "uvloop"

    uvicorn.run(**uvicorn_config)
