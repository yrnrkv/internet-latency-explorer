-- Enable TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Raw latency samples (hypertable)
CREATE TABLE IF NOT EXISTS latency_samples (
    time        TIMESTAMPTZ NOT NULL,
    probe_id    TEXT NOT NULL,
    probe_city  TEXT NOT NULL,
    probe_lat   DOUBLE PRECISION,
    probe_lng   DOUBLE PRECISION,
    target_name TEXT NOT NULL,
    target_host TEXT NOT NULL,
    target_city TEXT NOT NULL,
    target_lat  DOUBLE PRECISION,
    target_lng  DOUBLE PRECISION,
    target_type TEXT NOT NULL,
    latency_ms  DOUBLE PRECISION,
    jitter_ms   DOUBLE PRECISION,
    packet_loss DOUBLE PRECISION,
    http_status INTEGER
);

SELECT create_hypertable('latency_samples', 'time', if_not_exists => TRUE);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_latency_probe  ON latency_samples (probe_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_latency_target ON latency_samples (target_name, time DESC);
CREATE INDEX IF NOT EXISTS idx_latency_route  ON latency_samples (probe_city, target_city, time DESC);

-- Continuous aggregate: 1-minute rollup
CREATE MATERIALIZED VIEW IF NOT EXISTS latency_1m
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 minute', time) AS bucket,
    probe_id,
    probe_city,
    target_name,
    target_city,
    target_type,
    avg(latency_ms)  AS avg_ms,
    percentile_cont(0.5)  WITHIN GROUP (ORDER BY latency_ms) AS p50_ms,
    percentile_cont(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95_ms,
    percentile_cont(0.99) WITHIN GROUP (ORDER BY latency_ms) AS p99_ms,
    min(latency_ms)  AS min_ms,
    max(latency_ms)  AS max_ms,
    avg(packet_loss) AS packet_loss_avg,
    avg(jitter_ms)   AS jitter_avg,
    count(*)         AS sample_count
FROM latency_samples
GROUP BY bucket, probe_id, probe_city, target_name, target_city, target_type
WITH NO DATA;

-- Continuous aggregate: 1-hour rollup
CREATE MATERIALIZED VIEW IF NOT EXISTS latency_1h
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    probe_id,
    probe_city,
    target_name,
    target_city,
    target_type,
    avg(latency_ms)  AS avg_ms,
    percentile_cont(0.5)  WITHIN GROUP (ORDER BY latency_ms) AS p50_ms,
    percentile_cont(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95_ms,
    percentile_cont(0.99) WITHIN GROUP (ORDER BY latency_ms) AS p99_ms,
    min(latency_ms)  AS min_ms,
    max(latency_ms)  AS max_ms,
    avg(packet_loss) AS packet_loss_avg,
    avg(jitter_ms)   AS jitter_avg,
    count(*)         AS sample_count
FROM latency_samples
GROUP BY bucket, probe_id, probe_city, target_name, target_city, target_type
WITH NO DATA;

-- Probes registry
CREATE TABLE IF NOT EXISTS probes (
    probe_id   TEXT PRIMARY KEY,
    city       TEXT NOT NULL,
    lat        DOUBLE PRECISION,
    lng        DOUBLE PRECISION,
    api_key    TEXT NOT NULL,
    last_seen  TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Anomaly events
CREATE TABLE IF NOT EXISTS anomaly_events (
    id           SERIAL PRIMARY KEY,
    probe_id     TEXT NOT NULL,
    target_name  TEXT NOT NULL,
    anomaly_type TEXT NOT NULL,
    severity     TEXT NOT NULL,
    value        DOUBLE PRECISION,
    baseline     DOUBLE PRECISION,
    detected_at  TIMESTAMPTZ NOT NULL,
    resolved_at  TIMESTAMPTZ,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_anomaly_time ON anomaly_events (detected_at DESC);

-- Data retention: keep raw data for 7 days
SELECT add_retention_policy('latency_samples', INTERVAL '7 days', if_not_exists => TRUE);
