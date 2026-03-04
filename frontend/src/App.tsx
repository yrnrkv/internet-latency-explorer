import React from 'react'
import { Layout } from './components/Layout'
import { useLatencyHistory } from './hooks/useLatencyHistory'
import { useLatencyStream } from './hooks/useLatencyStream'
import { useProbes } from './hooks/useProbes'

export function App() {
  useLatencyStream()
  useProbes()
  useLatencyHistory()

  return <Layout />
}
