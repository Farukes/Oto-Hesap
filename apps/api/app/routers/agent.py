"""agent uçları — AGENTS.md §6 sözleşmesi. Sahibi: Ömer.

POST /api/agent/check -> {created, drafts, skipped}  (200; kural tabanlı, LLM yok)
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..services.agent import run_check

router = APIRouter(prefix="/api", tags=["agent"])
DbDep = Annotated[Session, Depends(get_db)]


@router.post("/agent/check")
def agent_check(db: DbDep) -> dict[str, Any]:
    """Kritik stoktaki ürünler için sipariş taslağı üretir (tekrar korumalı)."""
    return run_check(db)
