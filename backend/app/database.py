import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncpg

from app.config import settings

log = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None


_MIGRATIONS = """
CREATE TABLE IF NOT EXISTS latency_samples (
    time        TIMESTAMPTZ NOT NULL,
    probe_id    TEXT NOT NULL,
    probe_city  TEXT NOT NULL,
    probe_lat   DOUBLE PRECISION,
    probe_lng   DOUBLE PRECISION,
    target_name TEXT NOT NULL,
    target_host TEXT NOT NULL,
    target_city TEXT NOT NULL,
    target_lat  DOUBLE PRECISION,
    target_lng  DOUBLE PRECISION,
    target_type TEXT NOT NULL,
    latency_ms  DOUBLE PRECISION,
    jitter_ms   DOUBLE PRECISION,
    packet_loss DOUBLE PRECISION,
    http_status INTEGER
);

CREATE INDEX IF NOT EXISTS idx_latency_probe  ON latency_samples (probe_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_latency_target ON latency_samples (target_name, time DESC);
CREATE INDEX IF NOT EXISTS idx_latency_route  ON latency_samples (probe_city, target_city, time DESC);

CREATE TABLE IF NOT EXISTS probes (
    probe_id    TEXT PRIMARY KEY,
    city        TEXT NOT NULL,
    lat         DOUBLE PRECISION,
    lng         DOUBLE PRECISION,
    api_key     TEXT NOT NULL,
    last_seen   TIMESTAMPTZ,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS anomaly_events (
    id           SERIAL PRIMARY KEY,
    probe_id     TEXT NOT NULL,
    target_name  TEXT NOT NULL,
    anomaly_type TEXT NOT NULL,
    severity     TEXT NOT NULL,
    value        DOUBLE PRECISION,
    baseline     DOUBLE PRECISION,
    detected_at  TIMESTAMPTZ NOT NULL,
    resolved_at  TIMESTAMPTZ,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_anomaly_time ON anomaly_events (detected_at DESC);
"""


async def run_migrations() -> None:
    pool = await get_pool()
    try:
        async with pool.acquire() as conn:
            await conn.execute(_MIGRATIONS)
    except Exception:
        log.exception("Database migration failed")
        raise
    log.info("Database tables created/verified successfully")


async def init_db() -> None:
    global _pool
    dsn = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
    _pool = await asyncpg.create_pool(dsn=dsn, min_size=2, max_size=10)
    log.info("Database pool created")


async def close_db() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        log.info("Database pool closed")


async def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database pool not initialised")
    return _pool


@asynccontextmanager
async def acquire() -> AsyncGenerator[asyncpg.Connection, None]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        yield conn
