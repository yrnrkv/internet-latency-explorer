"""Redis-based sliding window rate limiter."""
import logging
import time

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

import redis.asyncio as aioredis

from app.config import settings
from app.services.streaming import _redis

log = logging.getLogger(__name__)


async def rate_limit_middleware(request: Request, call_next):
    if _redis is None:
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    key = f"rate:{client_ip}"
    now = int(time.time())
    window = 60  # seconds

    try:
        pipe = _redis.pipeline()
        pipe.zremrangebyscore(key, 0, now - window)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, window)
        results = await pipe.execute()
        count = results[2]
    except Exception as exc:
        log.warning("Rate limit check failed: %s", exc)
        return await call_next(request)

    if count > settings.rate_limit_per_minute:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Too many requests"},
            headers={"Retry-After": "60"},
        )
    return await call_next(request)
