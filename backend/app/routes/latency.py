from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

from fastapi import APIRouter, Query

from app.database import acquire

router = APIRouter()

RANGE_MAP = {
    "1h": timedelta(hours=1),
    "6h": timedelta(hours=6),
    "24h": timedelta(hours=24),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
}


@router.get("/latency")
async def get_latency(
    probe_id: Optional[str] = Query(None),
    target: Optional[str] = Query(None),
    range: Literal["1h", "6h", "24h", "7d", "30d"] = Query("1h"),
):
    delta = RANGE_MAP[range]
    since = datetime.now(timezone.utc) - delta

    conditions = ["time >= $1"]
    params: list = [since]
    idx = 2

    if probe_id:
        conditions.append(f"probe_id = ${idx}")
        params.append(probe_id)
        idx += 1
    if target:
        conditions.append(f"target_name = ${idx}")
        params.append(target)
        idx += 1

    where = " AND ".join(conditions)
    query = f"""
        SELECT time, probe_id, probe_city, probe_lat, probe_lng,
               target_name, target_city, target_lat, target_lng,
               target_type, latency_ms, jitter_ms, packet_loss, http_status
        FROM latency_samples
        WHERE {where}
        ORDER BY time DESC
        LIMIT 10000
    """

    async with acquire() as conn:
        rows = await conn.fetch(query, *params)

    return {"data": [dict(r) for r in rows]}


@router.get("/latency/summary")
async def get_latency_summary():
    """Latest reading per probe→target pair."""
    query = """
        SELECT DISTINCT ON (probe_id, target_name)
            time, probe_id, probe_city, probe_lat, probe_lng,
            target_name, target_city, target_lat, target_lng,
            target_type, latency_ms, jitter_ms, packet_loss, http_status
        FROM latency_samples
        ORDER BY probe_id, target_name, time DESC
    """
    async with acquire() as conn:
        rows = await conn.fetch(query)
    return {"data": [dict(r) for r in rows]}


@router.get("/latency/heatmap")
async def get_latency_heatmap(
    range: Literal["1h", "6h", "24h", "7d", "30d"] = Query("1h"),
):
    delta = RANGE_MAP[range]
    since = datetime.now(timezone.utc) - delta
    query = """
        SELECT probe_city, target_city,
               percentile_cont(0.5) WITHIN GROUP (ORDER BY latency_ms) AS p50_ms,
               avg(latency_ms) AS avg_ms,
               count(*) AS sample_count
        FROM latency_samples
        WHERE time >= $1
        GROUP BY probe_city, target_city
    """
    async with acquire() as conn:
        rows = await conn.fetch(query, since)
    return {"data": [dict(r) for r in rows]}
