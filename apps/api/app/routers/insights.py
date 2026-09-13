"""insights uçları — AGENTS.md §6 sözleşmesi. Sahibi: Yiğit.

GET /api/insights -> [{id, title, body, severity, metric, change_pct}] (en fazla 5, kural tabanlı)
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas.analytics import Insight
from ..services.insights import build_insights

router = APIRouter(prefix="/api", tags=["insights"])


@router.get("/insights", response_model=list[Insight])
def insights(db: Annotated[Session, Depends(get_db)]) -> list[Insight]:
    """Panodaki Öngörü kartları; LLM kullanılmaz, boş veride boş liste."""
    return build_insights(db)
