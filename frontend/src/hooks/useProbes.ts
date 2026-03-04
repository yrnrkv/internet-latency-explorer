import { useEffect } from 'react'
import { api } from '../api/client'
import { useLatencyStore } from '../stores/latencyStore'
import type { ProbeStatus } from '../types'

export function useProbes() {
  const setProbes = useLatencyStore((s) => s.setProbes)

  useEffect(() => {
    const fetchProbes = () =>
      api.getProbes().then((res) => setProbes(res.data as ProbeStatus[])).catch(console.error)

    fetchProbes()
    const interval = setInterval(fetchProbes, 30_000)
    return () => clearInterval(interval)
  }, [setProbes])
}
