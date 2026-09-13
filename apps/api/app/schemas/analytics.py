"""Analitik / Öngörü şemaları ve dönem tanımları (AGENTS.md §6, D16).

Dönem (`period`) yarı açık aralıktır [start, end):
  month   = içinde bulunulan takvim ayı (UTC)
  quarter = son 3 ay, başlangıç ay başına yuvarlanır (13 Eyl -> 1 Haz)
  half    = son 6 ay, başlangıç ay başına yuvarlanır (13 Eyl -> 1 Mar)  [varsayılan]
  end     = gelecek ayın 1'i 00:00 UTC
Para alanları JSON'da number (Decimal -> float).
"""

from __future__ import annotations

import calendar
from datetime import UTC, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator

Period = Literal["month", "quarter", "half"]
PERIODS: tuple[str, ...] = ("month", "quarter", "half")
PERIOD_MONTHS = {"month": 0, "quarter": 2, "half": 5}  # geriye kaç ay: pencere = N+1 takvim ayı
DEFAULT_PERIOD: Period = "half"
PERIOD_ERROR = "Geçersiz dönem; month, quarter veya half olmalı."


def months_ago(dt: datetime, n: int) -> datetime:
    """dt'den n takvim ayı geri (gün ayda yoksa ayın son günü)."""
    year, month = dt.year, dt.month - n
    while month <= 0:
        month += 12
        year -= 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def month_bounds(now: datetime | None = None) -> tuple[datetime, datetime, datetime]:
    """(geçen ay başı, bu ay başı, gelecek ay başı) — UTC takvim ayları, 00:00."""
    now = now or datetime.now(UTC)
    this = now.astimezone(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    prev = months_ago(this, 1)
    nxt = this.replace(year=this.year + this.month // 12, month=this.month % 12 + 1)
    return prev, this, nxt


def period_bounds(period: str, now: datetime | None = None) -> tuple[datetime, datetime]:
    """[start, end) — geçersiz dönemde ValueError."""
    if period not in PERIOD_MONTHS:
        raise ValueError(PERIOD_ERROR)
    _, this, nxt = month_bounds(now)
    return months_ago(this, PERIOD_MONTHS[period]), nxt


def period_start(period: str, now: datetime | None = None) -> datetime:
    return period_bounds(period, now)[0]


class _Money(BaseModel):
    @field_validator("*", mode="before")
    @classmethod
    def _decimal_to_float(cls, v: object) -> object:
        return float(v) if isinstance(v, Decimal) else v


class ExpenseByCategory(_Money):
    category: str
    amount: float
    share: float = Field(description="Toplam içindeki pay, yüzde 0–100 (1 ondalık)")


class SalesByProduct(_Money):
    product_id: int
    product: str
    revenue: float = Field(description="Σ sales.total")
    profit: float = Field(
        description="Tahmini brüt katkı: Σ qty × (unit_price − unit_cost), mevcut birim maliyetle"
    )
    qty: int


Severity = Literal["info", "warn", "critical"]


class Insight(BaseModel):
    id: str
    title: str
    body: str
    severity: Severity
    metric: str
    change_pct: float | None = None
