"""POST /api/assistant/ask ve GET /api/assistant/suggestions — AGENTS.md §6/§7. Sahibi: Murat."""

from __future__ import annotations

from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas.assistant import AskIn, AskOut
from ..services import text2sql
from ..services.llm import LLMError

router = APIRouter(prefix="/api", tags=["assistant"])

DbDep = Annotated[Session, Depends(get_db)]


@router.post("/assistant/ask", response_model=AskOut)
def ask_assistant(body: AskIn, db: DbDep) -> AskOut:
    question = body.question.strip()
    if not question:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Soru boş olamaz.")
    try:
        result = text2sql.ask(question, db)
    except text2sql.GuardError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=text2sql.GUARD_MESSAGE) from e
    except LLMError as e:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail=text2sql.UNAVAILABLE_MESSAGE
        ) from e
    return AskOut(**asdict(result))


@router.get("/assistant/suggestions", response_model=list[str])
def get_suggestions() -> list[str]:
    return text2sql.suggestions()
