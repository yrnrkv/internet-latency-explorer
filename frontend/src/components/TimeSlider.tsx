import React, { useState } from 'react'
import { useLatencyStore } from '../stores/latencyStore'

export function TimeSlider() {
  const pos = useLatencyStore((s) => s.timeSliderPosition)
  const setPos = useLatencyStore((s) => s.setTimeSliderPosition)
  const [playing, setPlaying] = useState(false)

  const togglePlay = () => setPlaying((p) => !p)

  return (
    <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-30 flex items-center gap-3 bg-slate-900/90 border border-white/10 rounded-full px-4 py-2 backdrop-blur">
      <button
        onClick={togglePlay}
        className="text-slate-300 hover:text-white text-sm w-6"
      >
        {playing ? '⏸' : '▶'}
      </button>
      <input
        type="range"
        min={0}
        max={1}
        step={0.001}
        value={pos}
        onChange={(e) => setPos(parseFloat(e.target.value))}
        className="w-48 accent-cyan-400"
      />
      <span className="text-xs font-mono text-slate-400">
        {pos >= 1 ? 'LIVE' : `${Math.round((1 - pos) * 24)}h ago`}
      </span>
    </div>
  )
}
