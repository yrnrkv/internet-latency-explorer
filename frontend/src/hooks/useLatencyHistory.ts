import { useEffect } from 'react'
import { api } from '../api/client'
import { useLatencyStore } from '../stores/latencyStore'
import type { LatencyTimeSeries } from '../types'

export function useLatencyHistory() {
  const selectedRoute = useLatencyStore((s) => s.selectedRoute)
  const selectedTimeRange = useLatencyStore((s) => s.selectedTimeRange)
  const setHistory = useLatencyStore((s) => s.setHistory)

  useEffect(() => {
    if (!selectedRoute) {
      setHistory([])
      return
    }
    const [probeId, targetName] = selectedRoute.split('→')
    api
      .getLatency({ probe_id: probeId, target: targetName, range: selectedTimeRange })
      .then((res) => {
        setHistory(
          (res.data as LatencyTimeSeries[]).slice().reverse(),
        )
      })
      .catch(console.error)
  }, [selectedRoute, selectedTimeRange, setHistory])
}
