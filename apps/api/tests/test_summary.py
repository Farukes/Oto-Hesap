"""GET /api/summary ve /api/cashflow/monthly — small_data ile sabit rakamlar.

small_data: satışlar 1/2/3/40/70/100 gün önce (1800, 600, 270, 900, 1200, 360);
giderler 1/5/45/80 gün önce (500, 3000, 3000, 700).
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

from sqlalchemy import select, text

from app.models import Expense, Sale

HALF_INCOME = 1800 + 600 + 270 + 900 + 1200 + 360  # 5130
HALF_EXPENSE = 500 + 3000 + 3000 + 700  # 7200
QUARTER_INCOME = 1800 + 600 + 270 + 900 + 1200  # 4770 (100 gün öncesi dışarıda)
# Çeyrek = içinde bulunulan ay dahil son 3 takvim ayı. Fixture'ın -70/-80 günlük satırları
# tarihe göre içeride/dışarıda kalır; beklenti pencere fonksiyonundan hesaplanır.


def _this_month_totals(db) -> tuple[float, float]:
    """Takvim ayı (UTC) beklentisi; testin koştuğu güne göre fixture'dan hesaplanır."""
    start = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    income = sum(float(s.total) for s in db.scalars(select(Sale)) if s.sold_at >= start)
    expense = sum(float(e.amount) for e in db.scalars(select(Expense)) if e.spent_at >= start)
    return income, expense


def test_summary_default_period_is_half(client, small_data):
    r = client.get("/api/summary")
    assert r.status_code == 200
    body = r.json()
    assert body["income"] == HALF_INCOME
    assert body["expense"] == HALF_EXPENSE
    assert body["net"] == HALF_INCOME - HALF_EXPENSE
    assert body["critical_count"] == 1
    assert isinstance(body["income"], float)
    datetime.fromisoformat(body["updated_at"])  # ISO 8601


def test_summary_half_explicit(client, small_data):
    body = client.get("/api/summary", params={"period": "half"}).json()
    assert (body["income"], body["expense"]) == (HALF_INCOME, HALF_EXPENSE)


def test_summary_quarter(client, small_data, db):
    from sqlalchemy import func, select

    from app.models import Expense, Sale
    from app.schemas.analytics import period_bounds

    start, end = period_bounds("quarter", datetime.now(UTC))
    exp_income = float(
        db.scalar(
            select(func.coalesce(func.sum(Sale.total), 0)).where(
                Sale.sold_at >= start, Sale.sold_at < end
            )
        )
    )
    exp_expense = float(
        db.scalar(
            select(func.coalesce(func.sum(Expense.amount), 0)).where(
                Expense.spent_at >= start, Expense.spent_at < end
            )
        )
    )
    body = client.get("/api/summary", params={"period": "quarter"}).json()
    assert body["income"] == exp_income
    assert body["expense"] == exp_expense
    assert body["net"] == round(exp_income - exp_expense, 2)
    assert exp_income <= HALF_INCOME and exp_expense <= HALF_EXPENSE
    assert body["critical_count"] == 1


def test_summary_month(client, db, small_data):
    income, expense = _this_month_totals(db)
    body = client.get("/api/summary", params={"period": "month"}).json()
    assert body["income"] == income
    assert body["expense"] == expense
    assert body["net"] == round(income - expense, 2)


def test_summary_invalid_period(client):
    assert client.get("/api/summary", params={"period": "year"}).status_code == 422


def test_summary_empty_db(client):
    body = client.get("/api/summary").json()
    assert body == {**body, "income": 0.0, "expense": 0.0, "net": 0.0, "critical_count": 0}


def test_cashflow_monthly_last_six_months(client, db, small_data):
    r = client.get("/api/cashflow/monthly")
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 6
    months = [row["month"] for row in rows]
    assert all(re.fullmatch(r"\d{4}-\d{2}", m) for m in months)
    assert months == sorted(months)
    current = db.execute(text("SELECT to_char(now(), 'YYYY-MM')")).scalar_one()
    assert months[-1] == current
    assert sum(row["income"] for row in rows) == HALF_INCOME
    assert sum(row["expense"] for row in rows) == HALF_EXPENSE
    for row in rows:
        assert row["net"] == row["income"] - row["expense"]


def test_cashflow_monthly_empty_db_is_zero_filled(client):
    rows = client.get("/api/cashflow/monthly").json()
    assert len(rows) == 6
    assert all(row["income"] == 0 and row["expense"] == 0 and row["net"] == 0 for row in rows)
