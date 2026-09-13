"""Çekirdek uçların Pydantic v2 şemaları: özet, nakit akışı, satış, gider, ürün.

Para alanları JSON'da number (float); istek gövdelerinde Decimal alınır (yuvarlama hatası yok).
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Period = Literal["month", "quarter", "half"]
Channel = Literal["magaza", "online"]


def to_utc(value: datetime) -> datetime:
    """DB oturumu hangi saat diliminde olursa olsun JSON'da UTC (AGENTS.md §6)."""
    return value.astimezone(UTC) if value.tzinfo else value.replace(tzinfo=UTC)


# --- özet / nakit akışı ---------------------------------------------------------------


class SummaryOut(BaseModel):
    income: float
    expense: float
    net: float
    critical_count: int
    updated_at: datetime


class CashflowMonthOut(BaseModel):
    month: str  # "YYYY-MM"
    income: float
    expense: float
    net: float


# --- satış ----------------------------------------------------------------------------


class SaleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sold_at: datetime
    product_id: int
    product_name: str
    qty: int
    unit_price: float
    total: float
    channel: str

    @field_validator("sold_at")
    @classmethod
    def _sold_at_utc(cls, value: datetime) -> datetime:
        return to_utc(value)


class SaleListOut(BaseModel):
    items: list[SaleOut]
    total: int


class SaleCreate(BaseModel):
    sold_at: datetime | None = None  # boşsa şimdi (UTC)
    product_id: int
    qty: int = Field(gt=0)
    unit_price: Decimal | None = Field(default=None, ge=0)  # boşsa ürünün sale_price'ı
    channel: Channel = "magaza"


class SaleUpdate(BaseModel):
    sold_at: datetime | None = None
    product_id: int | None = None
    qty: int | None = Field(default=None, gt=0)
    unit_price: Decimal | None = Field(default=None, ge=0)
    channel: Channel | None = None


# --- gider ----------------------------------------------------------------------------


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    spent_at: datetime
    category: str
    amount: float
    vendor: str | None
    note: str | None

    @field_validator("spent_at")
    @classmethod
    def _spent_at_utc(cls, value: datetime) -> datetime:
        return to_utc(value)


class ExpenseListOut(BaseModel):
    items: list[ExpenseOut]
    total: int


class ExpenseCreate(BaseModel):
    spent_at: datetime | None = None  # boşsa şimdi (UTC)
    category: str = Field(min_length=1)
    amount: Decimal = Field(gt=0)
    vendor: str | None = None
    note: str | None = None


class ExpenseUpdate(BaseModel):
    spent_at: datetime | None = None
    category: str | None = Field(default=None, min_length=1)
    amount: Decimal | None = Field(default=None, gt=0)
    vendor: str | None = None
    note: str | None = None


# --- ürün -----------------------------------------------------------------------------


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    unit_cost: float
    sale_price: float
    stock_qty: int
    reorder_point: int
    target_stock: int
    supplier_id: int | None
    supplier_name: str | None
    is_critical: bool
    open_order_id: int | None


class ProductPatch(BaseModel):
    reorder_point: int | None = Field(default=None, ge=0)
    target_stock: int | None = Field(default=None, ge=0)
    stock_qty: int | None = Field(default=None, ge=0)
