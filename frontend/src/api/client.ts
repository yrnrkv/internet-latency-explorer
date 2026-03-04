const BASE = import.meta.env.VITE_API_URL ?? ''

async function get<T>(path: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(`${BASE}${path}`, window.location.href)
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v))
  }
  const res = await fetch(url.toString())
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json() as Promise<T>
}

export const api = {
  getLatency: (params?: Record<string, string>) =>
    get<{ data: unknown[] }>('/api/v1/latency', params),
  getLatencySummary: () =>
    get<{ data: unknown[] }>('/api/v1/latency/summary'),
  getProbes: () =>
    get<{ data: unknown[] }>('/api/v1/probes'),
  getTargets: () =>
    get<{ data: unknown[] }>('/api/v1/targets'),
  getHeatmap: (range?: string) =>
    get<{ data: unknown[] }>('/api/v1/latency/heatmap', range ? { range } : undefined),
}
