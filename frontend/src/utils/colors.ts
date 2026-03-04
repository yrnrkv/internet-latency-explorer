/** Map latency in ms to a hex color. */
export function latencyColor(ms: number): [number, number, number, number] {
  if (ms <= 0) return [100, 100, 100, 180]
  if (ms < 50) return [34, 197, 94, 220]   // green
  if (ms < 150) return [234, 179, 8, 220]  // yellow
  if (ms < 300) return [249, 115, 22, 220] // orange
  return [239, 68, 68, 220]                // red
}

export function latencyColorHex(ms: number): string {
  if (ms <= 0) return '#64748b'
  if (ms < 50) return '#22c55e'
  if (ms < 150) return '#eab308'
  if (ms < 300) return '#f97316'
  return '#ef4444'
}

export function latencyLabel(ms: number): string {
  if (ms <= 0) return 'N/A'
  if (ms < 50) return 'Excellent'
  if (ms < 150) return 'Good'
  if (ms < 300) return 'Fair'
  return 'Poor'
}
