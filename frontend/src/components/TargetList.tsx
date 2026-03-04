import React, { useState } from 'react'
import { useLatencyStore } from '../stores/latencyStore'

const TYPE_COLORS: Record<string, string> = {
  service: 'text-cyan-400',
  cloud: 'text-purple-400',
  exchange: 'text-orange-400',
  city: 'text-green-400',
}

export function TargetList() {
  const liveReadings = useLatencyStore((s) => s.liveReadings)
  const selectRoute = useLatencyStore((s) => s.selectRoute)
  const selectedRoute = useLatencyStore((s) => s.selectedRoute)
  const [filter, setFilter] = useState<string>('all')

  const targets = Array.from(liveReadings.values())
  const filtered = filter === 'all' ? targets : targets.filter((t) => t.target_type === filter)

  return (
    <div className="flex flex-col h-full">
      <div className="flex gap-1 flex-wrap p-2 border-b border-white/10">
        {['all', 'service', 'cloud', 'exchange', 'city'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-2 py-0.5 rounded text-xs font-mono ${filter === f ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40' : 'text-slate-400 hover:text-slate-200'}`}
          >
            {f}
          </button>
        ))}
      </div>
      <div className="flex-1 overflow-y-auto">
        {filtered.map((t) => {
          const key = `${t.probe_id}→${t.target_name}`
          const isSelected = selectedRoute === key
          return (
            <button
              key={key}
              onClick={() => selectRoute(isSelected ? null : key)}
              className={`w-full text-left px-3 py-2 border-b border-white/5 hover:bg-white/5 transition-colors ${isSelected ? 'bg-cyan-500/10' : ''}`}
            >
              <div className="flex items-center justify-between">
                <span className={`text-xs font-mono ${TYPE_COLORS[t.target_type] ?? 'text-slate-300'}`}>
                  {t.target_name}
                </span>
                <span className="text-xs font-mono text-slate-400">
                  {t.latency_ms.toFixed(0)}ms
                </span>
              </div>
              <div className="text-xs text-slate-500 mt-0.5">{t.probe_city} → {t.target_city}</div>
            </button>
          )
        })}
        {filtered.length === 0 && (
          <div className="p-4 text-xs text-slate-500 text-center">No live data yet…</div>
        )}
      </div>
    </div>
  )
}
