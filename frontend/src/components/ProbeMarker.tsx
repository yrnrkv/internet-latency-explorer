import React from 'react'
import type { ProbeStatus } from '../types'

interface Props {
  probe: ProbeStatus
}

export function ProbeMarker({ probe }: Props) {
  return (
    <div className="relative">
      <div
        className={`w-3 h-3 rounded-full border-2 ${probe.is_online ? 'bg-green-400 border-green-300 animate-pulse' : 'bg-slate-500 border-slate-400'}`}
        title={`${probe.city} (${probe.is_online ? 'online' : 'offline'})`}
      />
    </div>
  )
}
