import React from 'react'
import { useLatencyStore } from '../stores/latencyStore'
import { LatencyPanel } from './LatencyPanel'
import { StatusBar } from './StatusBar'
import { TargetList } from './TargetList'
import { TimeSlider } from './TimeSlider'
import { WorldMap } from './WorldMap'

export function Layout() {
  const selectedRoute = useLatencyStore((s) => s.selectedRoute)
  const probes = useLatencyStore((s) => s.probes)
  const liveReadings = useLatencyStore((s) => s.liveReadings)
  const isConnected = useLatencyStore((s) => s.isConnected)
  const connectionFailed = useLatencyStore((s) => s.connectionFailed)

  const hasData = probes.length > 0 || liveReadings.size > 0

  const statusBadge = isConnected ? (
    <span className="px-2 py-0.5 bg-cyan-500/10 border border-cyan-500/30 rounded text-cyan-400">
      LIVE
    </span>
  ) : connectionFailed ? (
    <span className="px-2 py-0.5 bg-red-900/40 border border-red-700/50 rounded text-red-400">
      NO BACKEND
    </span>
  ) : hasData ? (
    <span className="px-2 py-0.5 bg-slate-700/50 border border-slate-600/50 rounded text-slate-400">
      DISCONNECTED
    </span>
  ) : (
    <span className="px-2 py-0.5 bg-slate-700/50 border border-slate-600/50 rounded text-slate-400">
      CONNECTING...
    </span>
  )

  return (
    <div className="h-screen w-screen bg-slate-950 text-slate-100 flex flex-col overflow-hidden">
      {/* Header */}
      <header className="flex-shrink-0 z-50 h-12 bg-slate-900/95 border-b border-white/10 flex items-center px-4 gap-3 backdrop-blur">
        <div className="flex items-center gap-2">
          <span className="text-cyan-400 text-lg">🌐</span>
          <span className="font-mono font-bold text-slate-100 tracking-tight">
            Internet Latency Explorer
          </span>
        </div>
        <div className="ml-auto flex items-center gap-2 text-xs text-slate-400 font-mono">
          {statusBadge}
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left sidebar — target list */}
        <aside className="w-56 flex-shrink-0 bg-slate-900/80 border-r border-white/10 flex flex-col overflow-hidden">
          <div className="p-2 border-b border-white/10 text-xs font-mono text-slate-400 uppercase tracking-wider">
            Targets
          </div>
          <TargetList />
        </aside>

        {/* Map */}
        <main className="flex-1 relative">
          <WorldMap />
          <TimeSlider />
        </main>

        {/* Right panel */}
        <aside
          className={`flex-shrink-0 bg-slate-900/90 border-l border-white/10 transition-all duration-300 ${
            selectedRoute ? 'w-72' : 'w-0 overflow-hidden'
          }`}
        >
          <LatencyPanel />
        </aside>
      </div>

      <StatusBar />
    </div>
  )
}
