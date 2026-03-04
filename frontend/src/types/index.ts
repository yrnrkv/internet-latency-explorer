export interface LatencySample {
  probe_id: string
  probe_city: string
  probe_lat: number
  probe_lng: number
  target_name: string
  target_host: string
  target_city: string
  target_lat: number
  target_lng: number
  target_type: 'service' | 'cloud' | 'city' | 'exchange'
  latency_ms: number
  jitter_ms: number
  packet_loss: number
  http_status: number | null
  timestamp: string
}

export interface ProbeStatus {
  probe_id: string
  city: string
  lat: number
  lng: number
  last_seen: string
  is_online: boolean
  targets_count: number
}

export interface AnomalyEvent {
  probe_id: string
  target_name: string
  anomaly_type: 'spike' | 'outage' | 'packet_loss'
  severity: 'warning' | 'critical'
  value: number
  baseline: number
  detected_at: string
}

export interface LatencyTimeSeries {
  time: string
  latency_ms: number
  jitter_ms: number
  packet_loss: number
}
