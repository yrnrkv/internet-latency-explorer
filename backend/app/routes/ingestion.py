import logging

from fastapi import APIRouter, Header, HTTPException

from app.database import acquire
from app.middleware.auth import verify_api_key
from app.models import IngestRequest, IngestResponse
from app.services.anomaly import check_anomaly
from app.services.streaming import publish_sample

log = logging.getLogger(__name__)
router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest(
    payload: IngestRequest,
    x_api_key: str = Header(..., alias="X-API-Key"),
) -> IngestResponse:
    verify_api_key(x_api_key)
    if not payload.samples:
        return IngestResponse(accepted=0)

    rows = [
        (
            s.timestamp,
            s.probe_id,
            s.probe_city,
            s.probe_lat,
            s.probe_lng,
            s.target_name,
            s.target_host,
            s.target_city,
            s.target_lat,
            s.target_lng,
            s.target_type,
            s.latency_ms,
            s.jitter_ms,
            s.packet_loss,
            s.http_status,
        )
        for s in payload.samples
    ]

    async with acquire() as conn:
        # Upsert probe registry
        for s in payload.samples:
            await conn.execute(
                """
                INSERT INTO probes (probe_id, city, lat, lng, api_key, last_seen)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (probe_id) DO UPDATE
                    SET last_seen = EXCLUDED.last_seen,
                        city = EXCLUDED.city
                """,
                s.probe_id,
                s.probe_city,
                s.probe_lat,
                s.probe_lng,
                x_api_key,
                s.timestamp,
            )

        # Batch insert — ON CONFLICT DO NOTHING for idempotency
        await conn.executemany(
            """
            INSERT INTO latency_samples
                (time, probe_id, probe_city, probe_lat, probe_lng,
                 target_name, target_host, target_city, target_lat, target_lng,
                 target_type, latency_ms, jitter_ms, packet_loss, http_status)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15)
            ON CONFLICT DO NOTHING
            """,
            rows,
        )

    # Publish to Redis stream and check anomalies
    for s in payload.samples:
        await publish_sample(s.model_dump(mode="json"))
        await check_anomaly(s)

    return IngestResponse(accepted=len(payload.samples))
