type MessageHandler = (data: unknown) => void

const WS_BASE = import.meta.env.VITE_WS_URL ?? `ws://${window.location.host}`

export class LatencyWebSocket {
  private ws: WebSocket | null = null
  private handlers: Set<MessageHandler> = new Set()
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private closed = false

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return
    const url = `${WS_BASE}/api/v1/ws/latency`
    this.ws = new WebSocket(url)

    this.ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data as string)
        if (data.type === 'ping') return
        this.handlers.forEach((h) => h(data))
      } catch {}
    }

    this.ws.onclose = () => {
      if (!this.closed) {
        this.reconnectTimer = setTimeout(() => this.connect(), 3000)
      }
    }
  }

  subscribe(handler: MessageHandler) {
    this.handlers.add(handler)
    return () => this.handlers.delete(handler)
  }

  close() {
    this.closed = true
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    this.ws?.close()
  }

  get isConnected() {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

export const wsClient = new LatencyWebSocket()
