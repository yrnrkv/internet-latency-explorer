import React from 'react'
import { useLatencyStore } from '../stores/latencyStore'
import { latencyColorHex, latencyLabel } from '../utils/colors'
import { AnomalyBadge } from './AnomalyBadge'
import { LatencyChart } from './LatencyChart'
import { StatsCard } from './StatsCard'

export function LatencyPanel() {
  const selectedRoute = useLatencyStore((s) => s.selectedRoute)
  const liveReadings = useLatencyStore((s) => s.liveReadings)
  const setTimeRange = useLatencyStore((s) => s.setTimeRange)
  const selectedTimeRange = useLatencyStore((s) => s.selectedTimeRange)
  const anomalies = useLatencyStore((s) => s.anomalies)

  if (!selectedRoute) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-slate-500 text-sm p-8 text-center">
        <div className="text-4xl mb-4">🌐</div>
        <p>Click on an arc or select a route from the list to see details.</p>
      </div>
    )
  }

  const reading = liveReadings.get(selectedRoute)
  const routeAnomalies = anomalies.filter(
    (a) => selectedRoute.includes(a.probe_id) && selectedRoute.includes(a.target_name),
  )

  return (
    <div className="flex flex-col gap-4 p-4 overflow-y-auto">
      <div>
        <div className="text-xs text-slate-500 font-mono mb-1">Route</div>
        <div className="text-sm font-mono text-slate-200">{selectedRoute}</div>
      </div>

      {reading && (
        <>
          <div className="text-center">
            <div
              className="text-5xl font-mono font-bold"
              style={{ color: latencyColorHex(reading.latency_ms) }}
            >
              {reading.latency_ms.toFixed(1)}
              <span className="text-lg font-normal text-slate-400 ml-1">ms</span>
            </div>
            <div className="text-xs text-slate-400 mt-1">{latencyLabel(reading.latency_ms)}</div>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <StatsCard label="Jitter" value={reading.jitter_ms} colorize={false} />
            <StatsCard
              label="Packet Loss"
              value={(reading.packet_loss * 100).toFixed(1)}
              unit="%"
              colorize={false}
            />
          </div>

          {routeAnomalies.length > 0 && (
            <div className="flex flex-col gap-1">
              <div className="text-xs text-slate-500">Recent Anomalies</div>
              {routeAnomalies.slice(0, 3).map((a, i) => (
                <AnomalyBadge key={i} type={a.anomaly_type} severity={a.severity} />
              ))}
            </div>
          )}
        </>
      )}

      <div>
        <div className="flex gap-1 mb-2">
          {(['1h', '6h', '24h', '7d'] as const).map((r) => (
            <button
              key={r}
              onClick={() => setTimeRange(r)}
              className={`px-2 py-0.5 rounded text-xs font-mono ${selectedTimeRange === r ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40' : 'text-slate-400 hover:text-slate-200'}`}
            >
              {r}
            </button>
          ))}
        </div>
        <LatencyChart />
      </div>
    </div>
  )
}
