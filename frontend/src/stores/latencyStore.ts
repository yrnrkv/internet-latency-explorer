import { create } from 'zustand'
import type { AnomalyEvent, LatencySample, LatencyTimeSeries, ProbeStatus } from '../types'

export type TimeRange = '1h' | '6h' | '24h' | '7d' | '30d'

interface LatencyStore {
  liveReadings: Map<string, LatencySample>
  probes: ProbeStatus[]
  selectedRoute: string | null
  selectedTimeRange: TimeRange
  history: LatencyTimeSeries[]
  anomalies: AnomalyEvent[]
  isConnected: boolean
  connectionFailed: boolean
  timeSliderPosition: number

  updateReading: (sample: LatencySample) => void
  setProbes: (probes: ProbeStatus[]) => void
  selectRoute: (routeKey: string | null) => void
  setTimeRange: (range: TimeRange) => void
  setHistory: (history: LatencyTimeSeries[]) => void
  setConnected: (v: boolean) => void
  setConnectionFailed: (v: boolean) => void
  setTimeSliderPosition: (v: number) => void
}

export const useLatencyStore = create<LatencyStore>((set) => ({
  liveReadings: new Map(),
  probes: [],
  selectedRoute: null,
  selectedTimeRange: '1h',
  history: [],
  anomalies: [],
  isConnected: false,
  connectionFailed: false,
  timeSliderPosition: 1,

  updateReading: (sample) =>
    set((state) => {
      const key = `${sample.probe_id}→${sample.target_name}`
      const next = new Map(state.liveReadings)
      next.set(key, sample)
      return { liveReadings: next }
    }),

  setProbes: (probes) => set({ probes }),
  selectRoute: (selectedRoute) => set({ selectedRoute }),
  setTimeRange: (selectedTimeRange) => set({ selectedTimeRange }),
  setHistory: (history) => set({ history }),
  setConnected: (isConnected) => set({ isConnected }),
  setConnectionFailed: (connectionFailed) => set({ connectionFailed }),
  setTimeSliderPosition: (timeSliderPosition) => set({ timeSliderPosition }),
}))
