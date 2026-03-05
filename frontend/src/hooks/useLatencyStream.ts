import { useEffect } from 'react'
import { wsClient } from '../api/websocket'
import { useLatencyStore } from '../stores/latencyStore'
import type { LatencySample } from '../types'

export function useLatencyStream() {
  const updateReading = useLatencyStore((s) => s.updateReading)
  const setConnected = useLatencyStore((s) => s.setConnected)
  const setConnectionFailed = useLatencyStore((s) => s.setConnectionFailed)

  useEffect(() => {
    wsClient.connect()

    const unsubscribe = wsClient.subscribe((data) => {
      updateReading(data as LatencySample)
    })

    const interval = setInterval(() => {
      setConnected(wsClient.isConnected)
      setConnectionFailed(wsClient.maxRetriesReached)
    }, 1000)

    return () => {
      unsubscribe()
      clearInterval(interval)
    }
  }, [updateReading, setConnected, setConnectionFailed])
}
