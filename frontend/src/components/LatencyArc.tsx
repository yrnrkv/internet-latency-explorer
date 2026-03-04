import React from 'react'
import { latencyColorHex } from '../utils/colors'
import type { LatencySample } from '../types'

interface Props {
  sample: LatencySample
}

/** Visual representation of a latency arc (used in panel/list views). */
export function LatencyArc({ sample }: Props) {
  const color = latencyColorHex(sample.latency_ms)
  return (
    <div className="flex items-center gap-2 p-2 bg-white/5 rounded-lg text-xs font-mono">
      <span className="text-slate-300">{sample.probe_city}</span>
      <span style={{ color }} className="flex-1 text-center">
        ──── {sample.latency_ms.toFixed(0)}ms ────
      </span>
      <span className="text-slate-300">{sample.target_city}</span>
    </div>
  )
}
