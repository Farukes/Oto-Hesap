"""Asistan (Text-to-SQL) şemaları — AGENTS.md §6 `/api/assistant/*`."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AskIn(BaseModel):
    question: str = Field(max_length=2000)


class AskOut(BaseModel):
    ok: bool
    answer: str
    sql: str | None
    rows: list[dict[str, Any]]
    columns: list[str]
    sources: list[str]
    asked_at: datetime
    cached: bool
    model: str  # "{provider}/{model}"; fake → "fake/none"


class SQLPlan(BaseModel):
    """LLM'den beklenen JSON: {"sql": "..."}; yanıtlanamıyorsa sql boş + refusal nedeni."""

    sql: str = ""
    refusal: str | None = None
