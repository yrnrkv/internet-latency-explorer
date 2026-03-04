"""Redis pub/sub streaming layer."""
import asyncio
import json
import logging
from typing import Callable, Coroutine

import redis.asyncio as aioredis

from app.config import settings

log = logging.getLogger(__name__)

CHANNEL = "latency:live"

_redis: aioredis.Redis | None = None
_subscribers: list[Callable] = []


def get_redis() -> aioredis.Redis | None:
    return _redis


async def init_redis() -> None:
    global _redis
    _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    log.info("Redis connected")


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


async def publish_sample(data: dict) -> None:
    if _redis is None:
        return
    try:
        await _redis.publish(CHANNEL, json.dumps(data, default=str))
    except Exception as exc:
        log.warning("Redis publish failed: %s", exc)


async def subscribe(callback: Callable[[str], Coroutine]) -> Callable:
    """Subscribe to the live latency channel. Returns an unsubscribe callable."""
    if _redis is None:
        return lambda: None

    pubsub = _redis.pubsub()
    await pubsub.subscribe(CHANNEL)

    async def _reader():
        async for message in pubsub.listen():
            if message["type"] == "message":
                await callback(message["data"])

    task = asyncio.create_task(_reader())

    async def _unsubscribe():
        task.cancel()
        await pubsub.unsubscribe(CHANNEL)
        await pubsub.aclose()

    return _unsubscribe
