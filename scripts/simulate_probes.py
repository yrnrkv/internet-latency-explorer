"""Run multiple simulated probes in a single process, sending to local API."""
import asyncio
import math
import os
import random
import time
from datetime import datetime, timezone

import aiohttp

API_URL = os.environ.get("API_URL", "http://localhost:8000")
API_KEY = os.environ.get("API_KEY", "dev-api-key")
INTERVAL = int(os.environ.get("INTERVAL_SECONDS", "10"))

PROBES = [
    {"id": "fra-1", "city": "Frankfurt", "lat": 50.110, "lng": 8.682},
    {"id": "nyc-1", "city": "New York", "lat": 40.713, "lng": -74.006},
    {"id": "sin-1", "city": "Singapore", "lat": 1.352, "lng": 103.820},
    {"id": "lax-1", "city": "Los Angeles", "lat": 34.052, "lng": -118.244},
    {"id": "lon-1", "city": "London", "lat": 51.507, "lng": -0.128},
]

TARGETS = [
    {"name": "Google DNS", "host": "8.8.8.8", "city": "Mountain View", "lat": 37.386, "lng": -122.084, "type": "service"},
    {"name": "Cloudflare", "host": "1.1.1.1", "city": "San Francisco", "lat": 37.774, "lng": -122.419, "type": "service"},
    {"name": "AWS us-east-1", "host": "ec2.us-east-1.amazonaws.com", "city": "Ashburn", "lat": 39.046, "lng": -77.487, "type": "cloud"},
    {"name": "AWS eu-west-1", "host": "ec2.eu-west-1.amazonaws.com", "city": "Dublin", "lat": 53.349, "lng": -6.260, "type": "cloud"},
    {"name": "AWS ap-northeast-1", "host": "ec2.ap-northeast-1.amazonaws.com", "city": "Tokyo", "lat": 35.682, "lng": 139.762, "type": "cloud"},
    {"name": "Frankfurt DE-CIX", "host": "de-cix.net", "city": "Frankfurt", "lat": 50.110, "lng": 8.682, "type": "exchange"},
    {"name": "Sydney", "host": "www.sydney.edu.au", "city": "Sydney", "lat": -33.868, "lng": 151.209, "type": "city"},
    {"name": "São Paulo", "host": "www.usp.br", "city": "São Paulo", "lat": -23.550, "lng": -46.634, "type": "city"},
]

R = 6371


def haversine_km(lat1, lng1, lat2, lng2):
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (math.sin(d_lat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def generate_sample(probe, target):
    dist = haversine_km(probe["lat"], probe["lng"], target["lat"], target["lng"])
    base = max(5.0, dist / 200 + random.gauss(8, 2))
    latency = base + random.gauss(0, base * 0.08)
    if random.random() < 0.02:
        latency *= random.uniform(3, 6)
    latency = max(1.0, latency)
    jitter = abs(random.gauss(0, latency * 0.05))
    packet_loss = 0.02 if random.random() < 0.01 else 0.0
    return {
        "probe_id": probe["id"],
        "probe_city": probe["city"],
        "probe_lat": probe["lat"],
        "probe_lng": probe["lng"],
        "target_name": target["name"],
        "target_host": target["host"],
        "target_city": target["city"],
        "target_lat": target["lat"],
        "target_lng": target["lng"],
        "target_type": target["type"],
        "latency_ms": round(latency, 3),
        "jitter_ms": round(jitter, 3),
        "packet_loss": round(packet_loss, 3),
        "http_status": 200,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def run_probe(session: aiohttp.ClientSession, probe: dict) -> None:
    samples = [generate_sample(probe, t) for t in TARGETS]
    try:
        async with session.post(
            f"{API_URL}/api/v1/ingest",
            json={"samples": samples},
            headers={"X-API-Key": API_KEY},
            timeout=aiohttp.ClientTimeout(total=10),
        ) as resp:
            if resp.status not in (200, 201):
                print(f"[{probe['id']}] Ingest returned {resp.status}")
            else:
                print(f"[{probe['id']}] Sent {len(samples)} samples")
    except Exception as exc:
        print(f"[{probe['id']}] Error: {exc}")


async def main():
    print(f"Simulator starting — {len(PROBES)} probes, {len(TARGETS)} targets, interval={INTERVAL}s")
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        while True:
            start = time.monotonic()
            await asyncio.gather(*[run_probe(session, p) for p in PROBES])
            elapsed = time.monotonic() - start
            await asyncio.sleep(max(0.0, INTERVAL - elapsed))


if __name__ == "__main__":
    asyncio.run(main())
