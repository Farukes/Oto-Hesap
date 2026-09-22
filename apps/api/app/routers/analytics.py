"""analytics uçları — AGENTS.md §6 sözleşmesi.

GET /api/analytics/expenses-by-category?period   -> [{category, amount, share}]
GET /api/analytics/sales-by-product?period&top    -> [{product_id, product, revenue, profit, qty}]
`period` yarı açık aralık [start, end) (schemas/analytics.py); `profit` = tahmini brüt katkı (D16).
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Expense, Product, Sale
from ..schemas.analytics import (
    DEFAULT_PERIOD,
    PERIOD_ERROR,
    PERIODS,
    ExpenseByCategory,
    SalesByProduct,
    period_bounds,
)

router = APIRouter(prefix="/api", tags=["analytics"])

TOP_MIN, TOP_MAX = 1, 50


def _bounds(period: str) -> tuple[datetime, datetime]:
    if period not in PERIODS:
        raise HTTPException(status_code=400, detail=PERIOD_ERROR)
    return period_bounds(period)


@router.get("/analytics/expenses-by-category", response_model=list[ExpenseByCategory])
def expenses_by_category(
    db: Annotated[Session, Depends(get_db)],
    period: str = Query(DEFAULT_PERIOD, description="month | quarter | half"),
) -> list[ExpenseByCategory]:
    """Dönemdeki giderlerin kategori dağılımı; `share` toplam içindeki yüzde (1 ondalık)."""
    start, end = _bounds(period)
    amount = func.sum(Expense.amount).label("amount")
    stmt = (
        select(Expense.category, amount)
        .where(Expense.spent_at >= start, Expense.spent_at < end)
        .group_by(Expense.category)
        .order_by(amount.desc(), Expense.category)
    )
    rows = db.execute(stmt).all()
    total = sum((r.amount for r in rows), start=0)
    return [
        ExpenseByCategory(
            category=r.category,
            amount=float(r.amount),
            share=round(float(r.amount) / float(total) * 100, 1) if total else 0.0,
        )
        for r in rows
    ]


@router.get("/analytics/sales-by-product", response_model=list[SalesByProduct])
def sales_by_product(
    db: Annotated[Session, Depends(get_db)],
    period: str = Query(DEFAULT_PERIOD, description="month | quarter | half"),
    top: int = Query(5, description=f"{TOP_MIN}–{TOP_MAX}"),
) -> list[SalesByProduct]:
    """Dönemde ciroya göre ilk `top` ürün; profit = SUM(qty * (unit_price - unit_cost))."""
    start, end = _bounds(period)
    if not TOP_MIN <= top <= TOP_MAX:
        raise HTTPException(status_code=400, detail=f"top {TOP_MIN} ile {TOP_MAX} arasında olmalı.")
    revenue = func.sum(Sale.total).label("revenue")
    profit = func.sum(Sale.qty * (Sale.unit_price - Product.unit_cost)).label("profit")
    qty = func.sum(Sale.qty).label("qty")
    stmt = (
        select(Product.id, Product.name, revenue, profit, qty)
        .join(Product, Product.id == Sale.product_id)
        .where(Sale.sold_at >= start, Sale.sold_at < end)
        .group_by(Product.id, Product.name)
        .order_by(revenue.desc(), Product.id)
        .limit(top)
    )
    return [
        SalesByProduct(
            product_id=r.id,
            product=r.name,
            revenue=float(r.revenue),
            profit=float(r.profit),
            qty=int(r.qty),
        )
        for r in db.execute(stmt).all()
    ]
