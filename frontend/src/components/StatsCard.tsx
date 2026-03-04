import React from 'react'
import { latencyColorHex } from '../utils/colors'

interface Props {
  label: string
  value: number | string
  unit?: string
  colorize?: boolean
}

export function StatsCard({ label, value, unit = 'ms', colorize = false }: Props) {
  const numVal = typeof value === 'number' ? value : parseFloat(String(value))
  const color = colorize && !isNaN(numVal) ? latencyColorHex(numVal) : '#e2e8f0'

  return (
    <div className="bg-white/5 border border-white/10 rounded-lg p-3 flex flex-col gap-1">
      <span className="text-xs text-slate-400 uppercase tracking-wider">{label}</span>
      <span
        className="text-2xl font-mono font-bold"
        style={{ color }}
      >
        {typeof value === 'number' ? value.toFixed(1) : value}
        <span className="text-sm font-normal text-slate-400 ml-1">{unit}</span>
      </span>
    </div>
  )
}
