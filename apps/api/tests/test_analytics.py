"""/api/analytics/* — conftest small_data ile sabit rakamlar; dönem = yarı açık [start, end)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.schemas.analytics import month_bounds, period_bounds

EXP = "/api/analytics/expenses-by-category"
SALES = "/api/analytics/sales-by-product"

# small_data satışları: (gün geri, ürün sırası, adet, birim fiyat); maliyetler 50 / 400 / 30
FIXTURE_SALES = (
    (1, 1, 2, 900),
    (2, 0, 5, 120),
    (3, 2, 3, 90),
    (40, 1, 1, 900),
    (70, 0, 10, 120),
    (100, 2, 4, 90),
)
FIXTURE_COSTS = (50, 400, 30)


def _ids(small_data) -> tuple[int, int, int]:
    p1, p2, p3 = small_data["products"]
    return p1.id, p2.id, p3.id


def _expected_sales(small_data, start: datetime) -> list[dict]:
    """Fixture satırlarını [start, ∞) penceresiyle elle toplar; ciroya göre azalan."""
    now = datetime.now(UTC)
    agg: dict[int, dict] = {}
    for days, idx, qty, price in FIXTURE_SALES:
        if now - timedelta(days=days) < start:
            continue
        p = small_data["products"][idx]
        row = agg.setdefault(
            idx, {"product_id": p.id, "product": p.name, "revenue": 0.0, "profit": 0.0, "qty": 0}
        )
        row["revenue"] += qty * price
        row["profit"] += qty * (price - FIXTURE_COSTS[idx])
        row["qty"] += qty
    return sorted(agg.values(), key=lambda r: (-r["revenue"], r["product_id"]))


def test_expenses_by_category_half(client, small_data):
    r = client.get(EXP)  # varsayılan period=half
    assert r.status_code == 200
    assert r.json() == [
        {"category": "kira", "amount": 6000.0, "share": 83.3},
        {"category": "elektrik", "amount": 700.0, "share": 9.7},
        {"category": "reklam", "amount": 500.0, "share": 6.9},
    ]
    # Çeyrek = içinde bulunulan ay dahil son 3 takvim ayı;
    # -80 günlük elektrik gideri çoğu tarihte dışarıda kalır.
    q = client.get(EXP, params={"period": "quarter"}).json()
    assert [row["category"] for row in q][:1] == ["kira"]
    assert all(row["amount"] <= 6000.0 for row in q)
    assert abs(sum(row["share"] for row in q) - 100.0) < 0.3


def test_sales_by_product_half(client, small_data):
    p1, p2, p3 = _ids(small_data)
    half = client.get(SALES, params={"period": "half"})
    assert half.status_code == 200
    assert half.json() == [
        {
            "product_id": p2,
            "product": "Powerbank 10000",
            "revenue": 2700.0,
            "profit": 1500.0,
            "qty": 3,
        },
        {
            "product_id": p1,
            "product": "USB-C Kablo",
            "revenue": 1800.0,
            "profit": 1050.0,
            "qty": 15,
        },
        {"product_id": p3, "product": "Silikon Kılıf", "revenue": 630.0, "profit": 420.0, "qty": 7},
    ]
    assert half.json() == _expected_sales(small_data, period_bounds("half")[0])


def test_sales_by_product_quarter(client, small_data):
    # Başlangıç ay başına yuvarlanır: -100 günlük satır güne göre içeride ya da dışarıda olabilir
    start = period_bounds("quarter")[0]
    assert start.day == 1 and start.hour == 0
    assert client.get(SALES, params={"period": "quarter"}).json() == _expected_sales(
        small_data, start
    )


@pytest.mark.skipif(datetime.now(UTC).day < 6, reason="fixture satırları ay başını aşar")
def test_period_month(client, small_data):
    p1, p2, p3 = _ids(small_data)
    assert client.get(EXP, params={"period": "month"}).json() == [
        {"category": "kira", "amount": 3000.0, "share": 85.7},
        {"category": "reklam", "amount": 500.0, "share": 14.3},
    ]
    sales = client.get(SALES, params={"period": "month"}).json()
    assert [(s["product_id"], s["revenue"], s["profit"], s["qty"]) for s in sales] == [
        (p2, 1800.0, 1000.0, 2),
        (p1, 600.0, 350.0, 5),
        (p3, 270.0, 180.0, 3),
    ]


def test_month_boundary_half_open(client, db):
    """Ayın 1'i 00:00 UTC bu aya; önceki ayın son saniyesi önceki aya."""
    from app.models import Expense, Product, Sale

    _, this, _ = month_bounds()
    p = Product(
        name="Sınır",
        category="aksesuar",
        unit_cost=Decimal("10"),
        sale_price=Decimal("20"),
        stock_qty=50,
        reorder_point=5,
        target_stock=20,
    )
    db.add(p)
    db.flush()
    db.add_all(
        [
            Sale(sold_at=this, product_id=p.id, qty=1, unit_price=20, total=20, channel="magaza"),
            Sale(
                sold_at=this - timedelta(seconds=1),
                product_id=p.id,
                qty=1,
                unit_price=20,
                total=20,
                channel="online",
            ),
            Expense(spent_at=this, category="kargo", amount=100),
            Expense(spent_at=this - timedelta(seconds=1), category="reklam", amount=900),
        ]
    )
    db.commit()
    sales = client.get(SALES, params={"period": "month"}).json()
    assert [(s["revenue"], s["qty"]) for s in sales] == [(20.0, 1)]
    exp = client.get(EXP, params={"period": "month"}).json()
    assert exp == [{"category": "kargo", "amount": 100.0, "share": 100.0}]
    assert {e["category"] for e in client.get(EXP, params={"period": "quarter"}).json()} == {
        "kargo",
        "reklam",
    }


def test_top_and_validation(client, small_data):
    _, p2, _ = _ids(small_data)
    top1 = client.get(SALES, params={"top": 1}).json()
    assert len(top1) == 1 and top1[0]["product_id"] == p2
    for bad in (0, 51):
        r = client.get(SALES, params={"top": bad})
        assert r.status_code == 400 and "top" in r.json()["detail"]
    for url in (EXP, SALES):
        r = client.get(url, params={"period": "year"})
        assert r.status_code == 400 and "dönem" in r.json()["detail"].lower()


def test_period_bounds_rounding():
    now = datetime(2026, 9, 13, 15, 30, tzinfo=UTC)
    assert period_bounds("month", now) == (
        datetime(2026, 9, 1, tzinfo=UTC),
        datetime(2026, 10, 1, tzinfo=UTC),
    )
    assert period_bounds("quarter", now) == (
        datetime(2026, 7, 1, tzinfo=UTC),
        datetime(2026, 10, 1, tzinfo=UTC),
    )
    assert period_bounds("half", now) == (
        datetime(2026, 4, 1, tzinfo=UTC),
        datetime(2026, 10, 1, tzinfo=UTC),
    )
    jan = datetime(2027, 1, 20, tzinfo=UTC)
    assert period_bounds("quarter", jan)[0] == datetime(2026, 11, 1, tzinfo=UTC)
    assert period_bounds("half", jan)[0] == datetime(2026, 8, 1, tzinfo=UTC)
    with pytest.raises(ValueError):
        period_bounds("year", now)


def test_empty_db(client):
    assert client.get(EXP).json() == []
    assert client.get(SALES).json() == []
