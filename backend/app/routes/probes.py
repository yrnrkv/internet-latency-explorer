from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException

from app.database import acquire

router = APIRouter()

ONLINE_THRESHOLD = timedelta(minutes=2)


@router.get("/probes")
async def list_probes():
    async with acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT p.probe_id, p.city, p.lat, p.lng, p.last_seen,
                   count(DISTINCT s.target_name) AS targets_count
            FROM probes p
            LEFT JOIN latency_samples s ON s.probe_id = p.probe_id
                AND s.time >= now() - INTERVAL '1 hour'
            GROUP BY p.probe_id, p.city, p.lat, p.lng, p.last_seen
            ORDER BY p.last_seen DESC NULLS LAST
            """
        )

    now = datetime.now(timezone.utc)
    result = []
    for r in rows:
        last_seen = r["last_seen"]
        is_online = (
            last_seen is not None and (now - last_seen) < ONLINE_THRESHOLD
        )
        result.append(
            {
                "probe_id": r["probe_id"],
                "city": r["city"],
                "lat": r["lat"],
                "lng": r["lng"],
                "last_seen": last_seen,
                "is_online": is_online,
                "targets_count": r["targets_count"],
            }
        )
    return {"data": result}


@router.get("/probes/{probe_id}")
async def get_probe(probe_id: str):
    async with acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM probes WHERE probe_id = $1", probe_id
        )
    if row is None:
        raise HTTPException(status_code=404, detail="Probe not found")
    return dict(row)
