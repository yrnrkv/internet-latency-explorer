import React from 'react'
import { useLatencyStore } from '../stores/latencyStore'

export function StatusBar() {
  const isConnected = useLatencyStore((s) => s.isConnected)
  const liveReadings = useLatencyStore((s) => s.liveReadings)
  const probes = useLatencyStore((s) => s.probes)
  const onlineProbes = probes.filter((p) => p.is_online).length

  return (
    <div className="fixed bottom-0 left-0 right-0 z-40 h-8 bg-slate-900/90 border-t border-white/10 flex items-center px-4 gap-6 text-xs text-slate-400">
      <span className="flex items-center gap-1.5">
        <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-500'}`} />
        {isConnected ? 'Connected' : 'Disconnected'}
      </span>
      <span>{onlineProbes} active probe{onlineProbes !== 1 ? 's' : ''}</span>
      <span>{liveReadings.size} live routes</span>
      <span className="ml-auto">Internet Latency Explorer</span>
    </div>
  )
}
