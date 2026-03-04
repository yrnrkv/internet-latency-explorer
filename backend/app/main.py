import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import close_db, init_db
from app.middleware.rate_limit import rate_limit_middleware
from app.routes import ingestion, latency, probes, targets, ws
from app.services.streaming import close_redis, init_redis

log = logging.getLogger(__name__)

app = FastAPI(title="Internet Latency Explorer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(rate_limit_middleware)


@app.on_event("startup")
async def startup() -> None:
    await init_db()
    await init_redis()


@app.on_event("shutdown")
async def shutdown() -> None:
    await close_db()
    await close_redis()


@app.get("/health")
async def health():
    return {"status": "ok"}


PREFIX = "/api/v1"
app.include_router(ingestion.router, prefix=PREFIX)
app.include_router(latency.router, prefix=PREFIX)
app.include_router(probes.router, prefix=PREFIX)
app.include_router(targets.router, prefix=PREFIX)
app.include_router(ws.router, prefix=PREFIX)
