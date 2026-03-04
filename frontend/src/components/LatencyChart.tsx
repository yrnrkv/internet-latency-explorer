import React from 'react'
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useLatencyStore } from '../stores/latencyStore'

export function LatencyChart() {
  const history = useLatencyStore((s) => s.history)

  if (history.length === 0) {
    return (
      <div className="flex items-center justify-center h-32 text-slate-500 text-sm">
        Select a route to view history
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={160}>
      <AreaChart data={history} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
        <defs>
          <linearGradient id="latencyGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#22d3ee" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis
          dataKey="time"
          tickFormatter={(v: string) => new Date(v).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          tick={{ fill: '#64748b', fontSize: 10 }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fill: '#64748b', fontSize: 10 }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8 }}
          labelStyle={{ color: '#94a3b8', fontSize: 11 }}
          itemStyle={{ color: '#22d3ee', fontFamily: 'monospace' }}
          formatter={(v: number) => [`${v.toFixed(1)} ms`, 'Latency']}
          labelFormatter={(label: string) => new Date(label).toLocaleTimeString()}
        />
        <Area
          type="monotone"
          dataKey="latency_ms"
          stroke="#22d3ee"
          strokeWidth={2}
          fill="url(#latencyGrad)"
          dot={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
