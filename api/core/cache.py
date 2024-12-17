import pickle
from functools import wraps
from typing import Any

import redis.asyncio as redis
from fastapi import Request

from api.config import settings


class RedisCache:
    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.redis = redis.from_url(redis_url)

    async def get(self, key: str) -> Any | None:
        value = await self.redis.get(key)
        if value:
            return pickle.loads(value)
        return None

    async def set(self, key: str, value: Any, expire: int = 300):
        await self.redis.set(key, pickle.dumps(value), ex=expire)

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def delete_pattern(self, pattern: str):
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)

    async def close(self):
        await self.redis.close()


def cache_response(expire: int = 300, prefix: str = ""):
    """Cache decorator for FastAPI endpoint responses"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            cache: RedisCache = request.app.state.cache

            key = f"{prefix}:{request.url.path}"
            if request.query_params:
                key += f":{str(request.query_params)}"

            cached_response = await cache.get(key)
            if cached_response is not None:
                return cached_response

            response = await func(*args, request=request, **kwargs)

            await cache.set(key, response, expire)
            return response

        return wrapper

    return decorator


# @router.get("/products/")
# @cache_response(expire=300, key_prefix="products")
# async def read_products(request: Request, db_session: DBSession):
