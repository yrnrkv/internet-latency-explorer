from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LatencySample(BaseModel):
    probe_id: str
    probe_city: str
    probe_lat: float
    probe_lng: float
    target_name: str
    target_host: str
    target_city: str
    target_lat: float
    target_lng: float
    target_type: str
    latency_ms: float = Field(ge=0)
    jitter_ms: float = Field(ge=0)
    packet_loss: float = Field(ge=0.0, le=1.0)
    http_status: Optional[int] = None
    timestamp: datetime


class IngestRequest(BaseModel):
    samples: list[LatencySample]


class IngestResponse(BaseModel):
    accepted: int
    message: str = "ok"


class LatencyAggregation(BaseModel):
    probe_id: str
    target_name: str
    p50_ms: float
    p95_ms: float
    p99_ms: float
    avg_ms: float
    min_ms: float
    max_ms: float
    packet_loss_avg: float
    sample_count: int
    period_start: datetime
    period_end: datetime


class ProbeStatus(BaseModel):
    probe_id: str
    city: str
    lat: float
    lng: float
    last_seen: datetime
    is_online: bool
    targets_count: int


class AnomalyEvent(BaseModel):
    probe_id: str
    target_name: str
    anomaly_type: str
    severity: str
    value: float
    baseline: float
    detected_at: datetime
