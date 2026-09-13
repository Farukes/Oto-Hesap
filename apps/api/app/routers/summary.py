"""GET /api/summary ve GET /api/cashflow/monthly — AGENTS.md §6. Sahibi: Murat."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Expense, Product, Sale
from ..schemas.analytics import period_bounds
from ..schemas.core import CashflowMonthOut, Period, SummaryOut

router = APIRouter(prefix="/api", tags=["summary"])

DbDep = Annotated[Session, Depends(get_db)]

# Son 6 ay (içinde bulunulan ay dahil); veri olmayan aylar 0 ile doldurulur.
# Ay sınırı görünümle (v_monthly_cashflow) aynı oturum saat dilimine göre hesaplanır.
_CASHFLOW_SQL = text(
    """
    SELECT to_char(m, 'YYYY-MM')   AS month,
           COALESCE(v.income, 0)   AS income,
           COALESCE(v.expense, 0)  AS expense,
           COALESCE(v.net, 0)      AS net
    FROM generate_series(
           date_trunc('month', now()) - interval '5 months',
           date_trunc('month', now()),
           interval '1 month') AS m
    LEFT JOIN v_monthly_cashflow v ON v.month = m
    ORDER BY m
    """
)


@router.get("/summary", response_model=SummaryOut)
def get_summary(db: DbDep, period: Annotated[Period, Query()] = "half") -> SummaryOut:
    now = datetime.now(UTC)
    start, end = period_bounds(
        period, now
    )  # takvim ayına hizalı, [start, end) — analytics ile aynı
    income = db.scalar(
        select(func.coalesce(func.sum(Sale.total), 0)).where(
            Sale.sold_at >= start, Sale.sold_at < end
        )
    )
    expense = db.scalar(
        select(func.coalesce(func.sum(Expense.amount), 0)).where(
            Expense.spent_at >= start, Expense.spent_at < end
        )
    )
    critical = db.scalar(
        select(func.count()).select_from(Product).where(Product.stock_qty <= Product.reorder_point)
    )
    income_f = float(income or 0)
    expense_f = float(expense or 0)
    return SummaryOut(
        income=income_f,
        expense=expense_f,
        net=round(income_f - expense_f, 2),
        critical_count=int(critical or 0),
        updated_at=now,
    )


@router.get("/cashflow/monthly", response_model=list[CashflowMonthOut])
def get_cashflow_monthly(db: DbDep) -> list[CashflowMonthOut]:
    rows = db.execute(_CASHFLOW_SQL).all()
    return [
        CashflowMonthOut(
            month=r.month, income=float(r.income), expense=float(r.expense), net=float(r.net)
        )
        for r in rows
    ]
