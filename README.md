# 🌐 Internet Latency Explorer

> A production-quality distributed network latency measurement and visualization platform — real-time animated globe, time-series charts, anomaly detection, and WebSocket streaming.

[![License: MIT](https://img.shields.io/badge/License-MIT-cyan.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61dafb)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178c6)](https://typescriptlang.org)

---

## ✨ Features

- **🗺️ Animated World Map** — deck.gl ArcLayer with color-coded latency arcs (green → red)
- **⚡ Real-time Streaming** — WebSocket pipeline from probe → Redis pub/sub → browser map update
- **📊 Time-series Charts** — Recharts area chart with p50/p95/p99 percentiles, zoomable
- **🔍 Anomaly Detection** — Automatic spike and outage detection (3σ rule + packet-loss threshold)
- **🌍 Distributed Probes** — Lightweight Python agents; offline buffering when API unreachable
- **🐳 One-command Setup** — `docker-compose up` brings up the entire stack
- **🛡️ Auth & Rate Limiting** — API key authentication, Redis sliding-window rate limiter

---

## 🏗️ Architecture

```
[Probe Agents] ──HTTP POST──► [Ingestion API]
                                     │
                               [TimescaleDB]        [Redis Pub/Sub]
                                     │                    │
                               [Query API]          [WS Handler]
                                     │                    │
                               ──────────────────────────────
                                          │
                                    [React UI]
                               (deck.gl Map + Recharts)
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose

### Run the full stack

```bash
git clone https://github.com/yrnrkv/internet-latency-explorer
cd internet-latency-explorer
docker-compose up
```

| Service   | URL                         |
|-----------|-----------------------------|
| Frontend  | http://localhost:3000       |
| API       | http://localhost:8000       |
| API Docs  | http://localhost:8000/docs  |

The probe simulator starts automatically and sends data every 10 seconds.

---

## 📂 Project Structure

```
internet-latency-explorer/
├── probes/              # Probe agent (Python + aiohttp)
├── backend/             # FastAPI backend
│   └── app/
│       ├── routes/      # ingestion, latency, probes, targets, WebSocket
│       ├── services/    # aggregation, anomaly detection, Redis streaming
│       └── middleware/  # API key auth, rate limiting
├── frontend/            # React 18 + TypeScript + deck.gl + Recharts
│   └── src/
│       ├── components/  # WorldMap, LatencyPanel, LatencyChart, etc.
│       ├── hooks/       # useLatencyStream, useLatencyHistory, useProbes
│       ├── stores/      # Zustand state management
│       └── utils/       # Color mapping, geo utilities
├── scripts/
│   ├── init_db.sql      # TimescaleDB schema + continuous aggregates
│   ├── seed_data.py     # 24h historical data seeder
│   └── simulate_probes.py  # Multi-probe simulator
└── docker-compose.yml
```

---

## 🌍 Probe Protocol

Probes send a JSON batch to `POST /api/v1/ingest` with `X-API-Key` header:

```json
{
  "samples": [
    {
      "probe_id": "fra-1",
      "probe_city": "Frankfurt",
      "probe_lat": 50.11,
      "probe_lng": 8.682,
      "target_name": "Google DNS",
      "target_host": "8.8.8.8",
      "target_city": "Mountain View",
      "target_lat": 37.386,
      "target_lng": -122.084,
      "target_type": "service",
      "latency_ms": 18.4,
      "jitter_ms": 0.9,
      "packet_loss": 0.0,
      "http_status": 200,
      "timestamp": "2024-01-01T12:00:00Z"
    }
  ]
}
```

### Probe Measurements
| Metric | Method |
|--------|--------|
| Latency | Median of N TCP connect times |
| Jitter | Std deviation of TCP connect times |
| Packet Loss | Failed connections / total attempts |
| HTTP TTFB | Full HTTPS GET time-to-first-byte |

### Offline Buffering
When the API is unreachable, probes buffer up to 1000 samples in memory and replay them once connectivity is restored.

---

## 📡 API Reference

### Ingestion
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/ingest` | Submit probe measurements (requires `X-API-Key`) |

### Latency
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/latency` | Raw latency time-series |
| `GET` | `/api/v1/latency/summary` | Latest reading per probe→target |
| `GET` | `/api/v1/latency/heatmap` | Aggregated probe×target matrix |

**Query parameters for `/latency`:**
- `probe_id` — filter by probe
- `target` — filter by target name
- `range` — `1h` | `6h` | `24h` | `7d` | `30d` (default: `1h`)

### Probes
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/probes` | List all probes with online status |
| `GET` | `/api/v1/probes/{id}` | Single probe details |

### Targets
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/targets` | List all known measurement targets |

### WebSocket
| Path | Description |
|------|-------------|
| `WS /api/v1/ws/latency` | Real-time latency stream |

---

## 🗄️ Data Model

### `latency_samples` (TimescaleDB hypertable)
| Column | Type | Description |
|--------|------|-------------|
| `time` | `TIMESTAMPTZ` | Measurement timestamp (partition key) |
| `probe_id` | `TEXT` | Source probe identifier |
| `target_name` | `TEXT` | Measurement target name |
| `latency_ms` | `DOUBLE` | Round-trip latency in milliseconds |
| `jitter_ms` | `DOUBLE` | Latency standard deviation |
| `packet_loss` | `DOUBLE` | Fraction of lost packets (0–1) |

Continuous aggregates (`latency_1m`, `latency_1h`) provide fast p50/p95/p99 queries.

---

## ⚖️ Design Decisions

### Why TimescaleDB over InfluxDB?
TimescaleDB is PostgreSQL — it supports standard SQL, JOINs, and familiar tooling. Continuous aggregates provide automatic time-bucketed rollups without a separate ETL pipeline. InfluxDB has better write throughput at very high cardinality, but for this workload (hundreds of probes × tens of targets), Postgres scales fine and is simpler to operate.

### Why WebSocket over SSE?
WebSocket enables bidirectional communication — future versions can push filter/subscription messages from browser to server. SSE is simpler for pure push, but WebSocket's ubiquity and the need for heartbeat/ping-pong make it the better long-term choice.

### Why Redis pub/sub over Kafka?
Redis is already in the stack for rate limiting. For sub-100 probes with 10-second intervals (~10 messages/second), Redis pub/sub has negligible overhead compared to Kafka's operational complexity. Kafka would be preferred at >10,000 messages/second or when replay/consumer groups are needed.

### Downsampling Strategy
Raw data is retained for 7 days via TimescaleDB's retention policy. Continuous aggregates (`latency_1m`, `latency_1h`) materialize rolled-up percentiles on disk, enabling fast dashboard queries without scanning raw samples.

---

## 🔥 Failure & Scale Considerations

| Scenario | Handling |
|----------|----------|
| Probe goes offline | `last_seen` tracked; `is_online` = false after 2 minutes |
| Duplicate probe data | `ON CONFLICT DO NOTHING` on `(probe_id, time)` — idempotent writes |
| 10× more probes | asyncpg connection pooling, batch inserts, Redis streams for fan-out |
| API abuse | Redis sliding-window rate limiter (60 req/min/IP) + API key auth |
| DB overload | Connection pool (max 10), continuous aggregates offload query pressure |

---

## 🚢 Deployment

### Local Development
```bash
docker-compose up
```

### Production
1. Replace `dev-api-key` with a strong random key in `docker-compose.yml`
2. Set `ALLOWED_ORIGINS` to your frontend domain
3. Point `API_URL` in each probe to your public backend URL
4. Configure a reverse proxy (nginx/Caddy) with TLS in front of the backend

### Deploying a Probe
```bash
docker run -d \
  -e PROBE_ID=lon-1 \
  -e PROBE_CITY=London \
  -e PROBE_LAT=51.507 \
  -e PROBE_LNG=-0.128 \
  -e API_URL=https://your-backend.example.com \
  -e API_KEY=your-secret-key \
  ghcr.io/yrnrkv/internet-latency-explorer/probe:latest
```

---

## 🧪 Running Tests

```bash
# Backend tests
cd backend && pip install -r requirements.txt && python -m pytest tests/ -v

# Probe tests  
cd probes && pip install -r requirements.txt && python -m pytest tests/ -v

# Frontend build check
cd frontend && npm install && npm run build
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Commit your changes: `git commit -m 'feat: add my feature'`
4. Push and open a Pull Request

---

## 📄 License

MIT © 2024 Internet Latency Explorer Contributors