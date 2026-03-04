"""Main probe agent — measures TCP/HTTP latency to configured targets."""

import asyncio
import json
import logging
import os
import socket
import statistics
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import aiohttp

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

# Offline buffer: store samples when API is unreachable
_buffer: deque = deque(maxlen=1000)


def load_targets() -> list[dict]:
    targets_path = Path(config.TARGETS_FILE)
    if not targets_path.is_absolute():
        targets_path = Path(__file__).parent / config.TARGETS_FILE
    with open(targets_path) as f:
        return json.load(f)["targets"]


async def tcp_ping(host: str, port: int, timeout: float = 5.0) -> Optional[float]:
    """Return TCP connect time in ms, or None on failure."""
    start = time.perf_counter()
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return (time.perf_counter() - start) * 1000
    except Exception:
        return None


async def http_latency(
    session: aiohttp.ClientSession, host: str, port: int, timeout: float = 10.0
) -> tuple[Optional[float], Optional[int]]:
    """Return (TTFB in ms, HTTP status) or (None, None) on failure."""
    scheme = "https" if port == 443 else "http"
    url = f"{scheme}://{host}/"
    start = time.perf_counter()
    try:
        async with session.get(
            url,
            timeout=aiohttp.ClientTimeout(total=timeout),
            ssl=False,
            allow_redirects=True,
        ) as resp:
            ttfb = (time.perf_counter() - start) * 1000
            return ttfb, resp.status
    except Exception:
        return None, None


async def measure_target(
    session: aiohttp.ClientSession, target: dict
) -> dict:
    host = target["host"]
    port = target["port"]

    # Multiple rapid TCP pings for jitter / packet-loss estimation
    pings = await asyncio.gather(
        *[tcp_ping(host, port) for _ in range(config.SAMPLES_PER_TARGET)]
    )
    successful = [p for p in pings if p is not None]
    packet_loss = 1.0 - (len(successful) / config.SAMPLES_PER_TARGET)

    if successful:
        latency_ms = statistics.median(successful)
        jitter_ms = statistics.stdev(successful) if len(successful) > 1 else 0.0
    else:
        latency_ms = 0.0
        jitter_ms = 0.0

    http_ms, http_status = await http_latency(session, host, port)
    if http_ms is not None and latency_ms == 0.0:
        latency_ms = http_ms

    return {
        "probe_id": config.PROBE_ID,
        "probe_city": config.PROBE_CITY,
        "probe_lat": config.PROBE_LAT,
        "probe_lng": config.PROBE_LNG,
        "target_name": target["name"],
        "target_host": host,
        "target_city": target["city"],
        "target_lat": target["lat"],
        "target_lng": target["lng"],
        "target_type": target["type"],
        "latency_ms": round(latency_ms, 3),
        "jitter_ms": round(jitter_ms, 3),
        "packet_loss": round(packet_loss, 3),
        "http_status": http_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def send_samples(
    session: aiohttp.ClientSession, samples: list[dict]
) -> bool:
    """POST samples to ingestion API. Returns True on success."""
    url = f"{config.API_URL}/api/v1/ingest"
    headers = {"X-API-Key": config.API_KEY, "Content-Type": "application/json"}
    try:
        async with session.post(
            url,
            json={"samples": samples},
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status in (200, 201):
                return True
            log.warning("Ingestion returned %s", resp.status)
            return False
    except Exception as exc:
        log.warning("Failed to send samples: %s", exc)
        return False


async def flush_buffer(session: aiohttp.ClientSession) -> None:
    """Try to send buffered samples from previous failed cycles."""
    if not _buffer:
        return
    batch = list(_buffer)
    if await send_samples(session, batch):
        _buffer.clear()
        log.info("Flushed %d buffered samples", len(batch))


async def run_cycle(session: aiohttp.ClientSession, targets: list[dict]) -> None:
    samples = await asyncio.gather(
        *[measure_target(session, t) for t in targets]
    )
    samples = list(samples)

    # Try to flush buffered data first
    await flush_buffer(session)

    if not await send_samples(session, samples):
        log.warning("API unreachable, buffering %d samples", len(samples))
        _buffer.extend(samples)
    else:
        log.info("Sent %d samples for probe %s", len(samples), config.PROBE_ID)


async def main() -> None:
    targets = load_targets()
    log.info(
        "Probe %s starting — %d targets, interval=%ds",
        config.PROBE_ID,
        len(targets),
        config.INTERVAL_SECONDS,
    )
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        while True:
            start = time.monotonic()
            try:
                await run_cycle(session, targets)
            except Exception as exc:
                log.error("Cycle error: %s", exc, exc_info=True)
            elapsed = time.monotonic() - start
            sleep_for = max(0.0, config.INTERVAL_SECONDS - elapsed)
            await asyncio.sleep(sleep_for)


if __name__ == "__main__":
    asyncio.run(main())
