import logging.config
from contextlib import asynccontextmanager

import uvicorn
from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.auth.dependencies import get_current_active_user
from api.auth.router import not_authenticated_router
from api.auth.router import router as auth_router
from api.catalogue.router import router as catalogue_router
from api.config import settings
from api.core.cache import RedisCache
from api.core.router import router as core_router
from api.export.router import router as export_router
from api.order.router import router as order_router
from api.review.router import router as review_router
from api.ticket.router import router as ticket_router
from api.ticket.router import ws_router
from api.user.router import router as user_router
from api.voucher.router import router as voucher_router

logging.config.dictConfig(settings.LOGGING_CONFIG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.cache = RedisCache(settings.REDIS_URL)
    yield
    await app.state.cache.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)


app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}


authenticated_router = APIRouter(dependencies=[Depends(get_current_active_user)])

authenticated_router.include_router(auth_router)
authenticated_router.include_router(user_router)
authenticated_router.include_router(catalogue_router)
authenticated_router.include_router(order_router)
authenticated_router.include_router(core_router)
authenticated_router.include_router(export_router)
authenticated_router.include_router(ticket_router)
authenticated_router.include_router(voucher_router)
authenticated_router.include_router(review_router)


app.include_router(authenticated_router)
app.include_router(not_authenticated_router)
app.include_router(ws_router)

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
