"""Seed TimescaleDB with 24 hours of simulated latency data."""
import math
import os
import random
import sys
from datetime import datetime, timedelta, timezone

import psycopg2

DB_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://latency:latency@localhost:5432/latency",
)

PROBES = [
    {"id": "fra-1", "city": "Frankfurt", "lat": 50.110, "lng": 8.682},
    {"id": "nyc-1", "city": "New York", "lat": 40.713, "lng": -74.006},
    {"id": "sin-1", "city": "Singapore", "lat": 1.352, "lng": 103.820},
]

TARGETS = [
    {"name": "Google DNS", "host": "8.8.8.8", "city": "Mountain View", "lat": 37.386, "lng": -122.084, "type": "service"},
    {"name": "Cloudflare", "host": "1.1.1.1", "city": "San Francisco", "lat": 37.774, "lng": -122.419, "type": "service"},
    {"name": "AWS us-east-1", "host": "ec2.us-east-1.amazonaws.com", "city": "Ashburn", "lat": 39.046, "lng": -77.487, "type": "cloud"},
    {"name": "AWS eu-west-1", "host": "ec2.eu-west-1.amazonaws.com", "city": "Dublin", "lat": 53.349, "lng": -6.260, "type": "cloud"},
    {"name": "AWS ap-northeast-1", "host": "ec2.ap-northeast-1.amazonaws.com", "city": "Tokyo", "lat": 35.682, "lng": 139.762, "type": "cloud"},
    {"name": "Frankfurt DE-CIX", "host": "de-cix.net", "city": "Frankfurt", "lat": 50.110, "lng": 8.682, "type": "exchange"},
]

R = 6371  # Earth radius km


def haversine_km(lat1, lng1, lat2, lng2):
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def base_latency(probe, target):
    dist = haversine_km(probe["lat"], probe["lng"], target["lat"], target["lng"])
    return max(5.0, dist / 200 + random.gauss(10, 3))


def simulate_latency(base, ts):
    hour = ts.hour
    peak_factor = 1.0 + 0.3 * math.sin((hour - 9) * math.pi / 12)
    ms = base * peak_factor + random.gauss(0, base * 0.1)
    # Occasional spike
    if random.random() < 0.02:
        ms *= random.uniform(3, 8)
    return max(1.0, ms)


def main():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=24)
    interval = timedelta(seconds=10)

    rows = []
    ts = start
    while ts <= now:
        for probe in PROBES:
            for target in TARGETS:
                base = base_latency(probe, target)
                latency = simulate_latency(base, ts)
                jitter = abs(random.gauss(0, latency * 0.05))
                packet_loss = 0.0
                if random.random() < 0.01:
                    packet_loss = random.uniform(0.1, 0.5)
                rows.append((
                    ts, probe["id"], probe["city"], probe["lat"], probe["lng"],
                    target["name"], target["host"], target["city"], target["lat"], target["lng"],
                    target["type"], round(latency, 3), round(jitter, 3), round(packet_loss, 3), 200,
                ))
        ts += interval

    cur.executemany(
        """
        INSERT INTO latency_samples
            (time, probe_id, probe_city, probe_lat, probe_lng,
             target_name, target_host, target_city, target_lat, target_lng,
             target_type, latency_ms, jitter_ms, packet_loss, http_status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT DO NOTHING
        """,
        rows,
    )

    # Upsert probes
    for probe in PROBES:
        cur.execute(
            """
            INSERT INTO probes (probe_id, city, lat, lng, api_key, last_seen)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (probe_id) DO UPDATE SET last_seen = EXCLUDED.last_seen
            """,
            (probe["id"], probe["city"], probe["lat"], probe["lng"], "dev-api-key", now),
        )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Seeded {len(rows)} samples for {len(PROBES)} probes × {len(TARGETS)} targets over 24h")


if __name__ == "__main__":
    main()
