"""Simple anomaly detection for latency spikes and packet loss."""
import logging
from collections import defaultdict, deque
from datetime import datetime, timezone

from app.database import acquire

log = logging.getLogger(__name__)

# Rolling window: last N samples per (probe_id, target_name)
_windows: dict[str, deque] = defaultdict(lambda: deque(maxlen=60))

SPIKE_STDDEV_MULTIPLIER = 3.0
OUTAGE_PACKET_LOSS_THRESHOLD = 0.5


async def check_anomaly(sample) -> None:
    key = f"{sample.probe_id}:{sample.target_name}"
    window = _windows[key]
    window.append(sample.latency_ms)

    if len(window) < 10:
        return  # Not enough data

    import statistics

    mean = statistics.mean(window)
    try:
        stdev = statistics.stdev(window)
    except statistics.StatisticsError:
        return

    anomaly_type = None
    severity = "warning"

    if stdev > 0 and sample.latency_ms > mean + SPIKE_STDDEV_MULTIPLIER * stdev:
        anomaly_type = "spike"
        severity = "critical" if sample.latency_ms > mean + 5 * stdev else "warning"
    elif sample.packet_loss >= OUTAGE_PACKET_LOSS_THRESHOLD:
        anomaly_type = "outage"
        severity = "critical"

    if anomaly_type:
        log.info(
            "Anomaly %s/%s on %s→%s: %.1fms (baseline %.1fms)",
            anomaly_type,
            severity,
            sample.probe_id,
            sample.target_name,
            sample.latency_ms,
            mean,
        )
        try:
            async with acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO anomaly_events
                        (probe_id, target_name, anomaly_type, severity,
                         value, baseline, detected_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    sample.probe_id,
                    sample.target_name,
                    anomaly_type,
                    severity,
                    sample.latency_ms,
                    mean,
                    datetime.now(timezone.utc),
                )
        except Exception as exc:
            log.warning("Failed to persist anomaly: %s", exc)
