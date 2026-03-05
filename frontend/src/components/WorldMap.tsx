import React, { useMemo } from 'react'
import DeckGL from '@deck.gl/react'
import { ArcLayer, ScatterplotLayer } from '@deck.gl/layers'
import Map from 'react-map-gl'
import { useLatencyStore } from '../stores/latencyStore'
import { latencyColor } from '../utils/colors'
import type { LatencySample } from '../types'

const INITIAL_VIEW = {
  longitude: 0,
  latitude: 20,
  zoom: 1.5,
  pitch: 30,
  bearing: 0,
}

// Use CartoDB dark-matter tiles (no token required)
const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json'

interface ArcDatum {
  sourcePosition: [number, number]
  targetPosition: [number, number]
  color: [number, number, number, number]
  sample: LatencySample
}

export function WorldMap() {
  const liveReadings = useLatencyStore((s) => s.liveReadings)
  const selectRoute = useLatencyStore((s) => s.selectRoute)
  const selectedRoute = useLatencyStore((s) => s.selectedRoute)
  const probes = useLatencyStore((s) => s.probes)

  const arcs: ArcDatum[] = useMemo(() => {
    return Array.from(liveReadings.values()).map((s) => ({
      sourcePosition: [s.probe_lng, s.probe_lat] as [number, number],
      targetPosition: [s.target_lng, s.target_lat] as [number, number],
      color: latencyColor(s.latency_ms),
      sample: s,
    }))
  }, [liveReadings])

  const layers = [
    new ArcLayer<ArcDatum>({
      id: 'latency-arcs',
      data: arcs,
      getSourcePosition: (d) => d.sourcePosition,
      getTargetPosition: (d) => d.targetPosition,
      getSourceColor: (d) => d.color,
      getTargetColor: (d) => d.color,
      getWidth: 2,
      pickable: true,
      autoHighlight: true,
      highlightColor: [255, 255, 255, 80],
      onClick: (info) => {
        if (info.object) {
          const s = (info.object as ArcDatum).sample
          const key = `${s.probe_id}→${s.target_name}`
          selectRoute(selectedRoute === key ? null : key)
        }
      },
    }),
    new ScatterplotLayer({
      id: 'probe-dots',
      data: probes,
      getPosition: (d: { lng: number; lat: number }) => [d.lng, d.lat] as [number, number],
      getRadius: 30000,
      getFillColor: (d: { is_online: boolean }) =>
        d.is_online ? [34, 197, 94, 220] : [100, 116, 139, 200],
      pickable: false,
      stroked: true,
      getLineColor: [255, 255, 255, 60],
      lineWidthMinPixels: 1,
    }),
  ]

  const hasData = arcs.length > 0 || probes.length > 0

  return (
    <div className="relative w-full h-full">
      <DeckGL
        initialViewState={INITIAL_VIEW}
        controller={true}
        layers={layers}
        getTooltip={(info) => {
          if (!info.object) return null
          const s = (info.object as ArcDatum).sample
          return {
            html: `
              <div style="font-family:monospace;font-size:12px;line-height:1.6">
                <b>${s.probe_city} → ${s.target_city}</b><br/>
                Latency: ${s.latency_ms.toFixed(1)} ms<br/>
                Jitter: ${s.jitter_ms.toFixed(1)} ms<br/>
                Packet Loss: ${(s.packet_loss * 100).toFixed(0)}%<br/>
                Target: ${s.target_name}
              </div>
            `,
            style: {
              backgroundColor: '#0f172a',
              border: '1px solid #1e293b',
              borderRadius: '8px',
              padding: '8px 12px',
              color: '#e2e8f0',
            },
          }
        }}
      >
        <Map mapStyle={MAP_STYLE} />
      </DeckGL>
      {!hasData && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="bg-slate-900/80 border border-white/10 rounded-lg px-6 py-4 text-center">
            <p className="text-slate-300 font-mono text-sm">No data available</p>
            <p className="text-slate-500 font-mono text-xs mt-1">
              Connect a backend to see latency data
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
