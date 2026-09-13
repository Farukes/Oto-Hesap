"""export uçları — AGENTS.md §6 sözleşmesi. Sahibi: Yiğit.

GET /api/export/sales.csv · GET /api/export/expenses.csv
Excel (TR) uyumlu: UTF-8 BOM, `;` ayraç, ondalık virgül, tarih `YYYY-MM-DD HH:MM` (UTC).
Formül enjeksiyonu: metin hücresi = + - @ sekme CR ile başlıyorsa başına `'` konur (sayılar hariç).
"""

from __future__ import annotations

import csv
import io
from collections.abc import Iterable
from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Expense, Product, Sale

router = APIRouter(prefix="/api", tags=["export"])

BOM = "﻿"
SALES_HEADER = ("Tarih", "Ürün", "Adet", "Birim Fiyat", "Toplam", "Kanal")
EXPENSES_HEADER = ("Tarih", "Kategori", "Tutar", "Tedarikçi", "Not")
FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def fmt_date(dt: datetime) -> str:
    return dt.astimezone(UTC).strftime("%Y-%m-%d %H:%M")


def fmt_amount(value: Decimal | float | int) -> str:
    """1234.5 -> '1234,50' (Excel TR ondalık virgül; binlik ayracı yok)."""
    return f"{Decimal(value):.2f}".replace(".", ",")


def safe_text(value: str | None) -> str:
    """Excel/Sheets formül olarak yorumlamasın: tehlikeli önekli metnin başına `'`."""
    text = value or ""
    return f"'{text}" if text.startswith(FORMULA_PREFIXES) else text


def to_csv(header: Iterable[str], rows: Iterable[Iterable[object]]) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";", lineterminator="\r\n", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(header)
    writer.writerows(rows)
    return (BOM + buf.getvalue()).encode("utf-8")


def csv_response(filename: str, body: bytes) -> Response:
    return Response(
        content=body,
        media_type="text/csv",  # Starlette charset=utf-8 ekler
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/sales.csv")
def export_sales(db: Annotated[Session, Depends(get_db)]) -> Response:
    stmt = (
        select(Sale.sold_at, Product.name, Sale.qty, Sale.unit_price, Sale.total, Sale.channel)
        .join(Product, Product.id == Sale.product_id)
        .order_by(Sale.sold_at, Sale.id)
    )
    rows = (
        (
            fmt_date(r.sold_at),
            safe_text(r.name),
            r.qty,
            fmt_amount(r.unit_price),
            fmt_amount(r.total),
            safe_text(r.channel),
        )
        for r in db.execute(stmt)
    )
    return csv_response("satislar.csv", to_csv(SALES_HEADER, rows))


@router.get("/export/expenses.csv")
def export_expenses(db: Annotated[Session, Depends(get_db)]) -> Response:
    stmt = select(
        Expense.spent_at, Expense.category, Expense.amount, Expense.vendor, Expense.note
    ).order_by(Expense.spent_at, Expense.id)
    rows = (
        (
            fmt_date(r.spent_at),
            safe_text(r.category),
            fmt_amount(r.amount),
            safe_text(r.vendor),
            safe_text(r.note),
        )
        for r in db.execute(stmt)
    )
    return csv_response("giderler.csv", to_csv(EXPENSES_HEADER, rows))
