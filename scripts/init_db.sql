-- Raw latency samples
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

-- Indexes
CREATE INDEX IF NOT EXISTS idx_latency_probe  ON latency_samples (probe_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_latency_target ON latency_samples (target_name, time DESC);
CREATE INDEX IF NOT EXISTS idx_latency_route  ON latency_samples (probe_city, target_city, time DESC);

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
