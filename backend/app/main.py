import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import close_db, init_db
from app.middleware.rate_limit import rate_limit_middleware
from app.routes import ingestion, latency, probes, targets, ws
from app.services.streaming import close_redis, init_redis

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_redis()
    yield
    await close_db()
    await close_redis()


app = FastAPI(title="Internet Latency Explorer API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(rate_limit_middleware)


@app.get("/health")
async def health():
    return {"status": "ok"}


PREFIX = "/api/v1"
app.include_router(ingestion.router, prefix=PREFIX)
app.include_router(latency.router, prefix=PREFIX)
app.include_router(probes.router, prefix=PREFIX)
app.include_router(targets.router, prefix=PREFIX)
app.include_router(ws.router, prefix=PREFIX)
