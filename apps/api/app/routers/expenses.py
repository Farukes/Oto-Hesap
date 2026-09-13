"""Gider CRUD — AGENTS.md §6 (satışla aynı kalıp). Sahibi: Murat."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Expense
from ..schemas.core import ExpenseCreate, ExpenseListOut, ExpenseOut, ExpenseUpdate
from .sales import as_utc

router = APIRouter(prefix="/api", tags=["expenses"])

DbDep = Annotated[Session, Depends(get_db)]

EXPENSE_NOT_FOUND = "Gider bulunamadı"


def _get_expense(db: Session, expense_id: int) -> Expense:
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=EXPENSE_NOT_FOUND)
    return expense


@router.get("/expenses", response_model=ExpenseListOut)
def list_expenses(
    db: DbDep,
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    q: Annotated[str | None, Query()] = None,
) -> ExpenseListOut:
    base = select(Expense)
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        base = base.where(
            or_(
                Expense.category.ilike(pattern),
                Expense.vendor.ilike(pattern),
                Expense.note.ilike(pattern),
            )
        )
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    items = db.scalars(
        base.order_by(Expense.spent_at.desc(), Expense.id.desc()).limit(limit).offset(offset)
    ).all()
    return ExpenseListOut(items=[ExpenseOut.model_validate(e) for e in items], total=int(total))


@router.post("/expenses", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(body: ExpenseCreate, db: DbDep) -> ExpenseOut:
    expense = Expense(
        spent_at=as_utc(body.spent_at),
        category=body.category.strip(),
        amount=body.amount,
        vendor=body.vendor,
        note=body.note,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return ExpenseOut.model_validate(expense)


@router.put("/expenses/{expense_id}", response_model=ExpenseOut)
def update_expense(expense_id: int, body: ExpenseUpdate, db: DbDep) -> ExpenseOut:
    expense = _get_expense(db, expense_id)
    data = body.model_dump(exclude_unset=True)
    if data.get("spent_at") is not None:
        expense.spent_at = as_utc(data["spent_at"])
    if data.get("category") is not None:
        expense.category = data["category"].strip()
    if data.get("amount") is not None:
        expense.amount = data["amount"]
    if "vendor" in data:  # null gönderilirse temizlenir
        expense.vendor = data["vendor"]
    if "note" in data:
        expense.note = data["note"]
    db.commit()
    db.refresh(expense)
    return ExpenseOut.model_validate(expense)


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: DbDep) -> Response:
    expense = _get_expense(db, expense_id)
    db.delete(expense)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
