import React from 'react'

interface Props {
  type: string
  severity: string
}

export function AnomalyBadge({ type, severity }: Props) {
  const bg = severity === 'critical' ? 'bg-red-500/20 border-red-500/50 text-red-400' : 'bg-yellow-500/20 border-yellow-500/50 text-yellow-400'
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full border text-xs font-mono ${bg}`}>
      {severity === 'critical' ? '⚠️' : '⚡'} {type}
    </span>
  )
}
