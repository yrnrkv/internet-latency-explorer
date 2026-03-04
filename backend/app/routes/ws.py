import asyncio
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.streaming import subscribe

log = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/latency")
async def ws_latency(websocket: WebSocket):
    await websocket.accept()
    queue: asyncio.Queue = asyncio.Queue(maxsize=500)

    async def _enqueue(msg: str) -> None:
        try:
            queue.put_nowait(msg)
        except asyncio.QueueFull:
            pass  # drop oldest messages under pressure

    unsub = await subscribe(_enqueue)
    try:
        heartbeat_task = asyncio.create_task(_heartbeat(websocket))
        while True:
            msg = await asyncio.wait_for(queue.get(), timeout=30)
            await websocket.send_text(msg)
    except (WebSocketDisconnect, asyncio.TimeoutError):
        pass
    except Exception as exc:
        log.warning("WS error: %s", exc)
    finally:
        heartbeat_task.cancel()
        await unsub()


async def _heartbeat(ws: WebSocket) -> None:
    while True:
        await asyncio.sleep(15)
        try:
            await ws.send_text(json.dumps({"type": "ping"}))
        except Exception:
            break
