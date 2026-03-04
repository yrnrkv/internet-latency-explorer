from fastapi import APIRouter

from app.database import acquire

router = APIRouter()


@router.get("/targets")
async def list_targets():
    async with acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT DISTINCT target_name, target_host, target_city,
                            target_lat, target_lng, target_type
            FROM latency_samples
            ORDER BY target_name
            """
        )
    return {"data": [dict(r) for r in rows]}
