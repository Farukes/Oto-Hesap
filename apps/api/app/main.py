"""OtoHesap API giriş noktası. CORS, istek logu, hata gövdesi, router kayıtları, sağlık ucu."""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import db
from .config import settings
from .routers import (
    agent,
    analytics,
    assistant,
    expenses,
    export,
    insights,
    orders,
    products,
    sales,
    summary,
)
from .services import llm

logging.basicConfig(
    level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
log = logging.getLogger("otohesap")


@asynccontextmanager
async def lifespan(_: FastAPI):
    sched = None
    if settings.agent_scheduler_enabled:
        from .services.scheduler import start_scheduler

        sched = start_scheduler()
    yield
    if sched is not None:
        sched.shutdown(wait=False)


app = FastAPI(title="OtoHesap API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    t0 = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - t0) * 1000
    log.info("%s %s -> %s (%.0f ms)", request.method, request.url.path, response.status_code, ms)
    return response


@app.exception_handler(Exception)
async def unhandled(_: Request, exc: Exception):
    log.exception("beklenmeyen hata: %s", exc)
    return JSONResponse(
        status_code=500, content={"detail": "Sunucu hatası; lütfen tekrar deneyin."}
    )


ROUTERS = (
    summary,
    sales,
    expenses,
    products,
    analytics,
    assistant,
    orders,
    agent,
    export,
    insights,
)
for r in ROUTERS:
    app.include_router(r.router)


@app.get("/api/health", tags=["health"])
def health() -> dict:
    return {
        "status": "ok",
        "db": db.db_ok(),
        "llm": llm.provider_name(),
        "scheduler": settings.agent_scheduler_enabled,
        "version": app.version,
    }
