"""data/seed.py — sayım, kritik stok, kâr lideri ve determinizm (TEST_DB_NAME veritabanında)."""

from __future__ import annotations

import importlib.util
import os
import pathlib
import sys
from datetime import UTC, datetime
from decimal import Decimal
from types import ModuleType

import psycopg
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[3]
SEED_PATH = ROOT / "data" / "seed.py"


def _load_seed() -> ModuleType:
    spec = importlib.util.spec_from_file_location("otohesap_seed", SEED_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclass, modülü sys.modules'ta arar
    spec.loader.exec_module(module)
    return module


seed = _load_seed()
URL = os.environ["DATABASE_URL"]  # conftest test veritabanına yönlendirdi


def _strip(summary: dict) -> dict:
    return {k: v for k, v in summary.items() if k != "seconds"}


@pytest.fixture(scope="module")
def seeded() -> tuple[dict, dict]:
    first = seed.run(URL, reset=True)
    second = seed.run(URL, reset=True)
    yield first, second
    with psycopg.connect(URL, autocommit=True) as conn:
        conn.execute(seed.TRUNCATE_SQL)


def _q(sql: str) -> list[tuple]:
    with psycopg.connect(URL) as conn:
        return conn.execute(sql).fetchall()


def test_counts(seeded):
    summary, _ = seeded
    assert summary["products"] == 20
    assert summary["suppliers"] == 5
    assert 540 <= summary["sales_rows"] <= 660
    assert 220 <= summary["expense_rows"] <= 280
    assert summary["seconds"] < 10
    assert summary["as_of"] == _q("SELECT MAX(sold_at)::date FROM sales")[0][0].isoformat()
    assert summary["as_of"].startswith("2026-09")
    n_sales = _q("SELECT COUNT(*) FROM sales")[0][0]
    n_exp = _q("SELECT COUNT(*) FROM expenses")[0][0]
    assert (n_sales, n_exp) == (summary["sales_rows"], summary["expense_rows"])


def test_deterministic(seeded):
    first, second = seeded
    assert _strip(first) == _strip(second)
    assert first["leader_fix_rows"] == 0, "lider farkı doğal olarak sağlanmalı"


def test_categories_and_margins(seeded):
    rows = _q("SELECT category, COUNT(*), MIN(unit_cost), MAX(unit_cost) FROM products GROUP BY 1")
    assert {r[0] for r in rows} == {"kulaklik", "kilif", "kablo-sarj", "powerbank", "aksesuar"}
    assert all(r[1] == 4 for r in rows)
    for cost, price in _q("SELECT unit_cost, sale_price FROM products"):
        assert Decimal("30") <= cost <= Decimal("1500")
        assert Decimal("0.25") <= (price - cost) / cost <= Decimal("0.60")


def test_suppliers(seeded):
    rows = _q("SELECT contact_channel, contact_address, lead_time_days FROM suppliers")
    telegram = [r for r in rows if r[0] == "telegram"]
    assert len(telegram) == 1 and telegram[0][1] == "TELEGRAM_CHAT_ID"
    assert all(r[0] == "email" and "@" in r[1] for r in rows if r[0] != "telegram")
    assert all(2 <= r[2] <= 7 for r in rows)


def test_stock_levels(seeded):
    summary, _ = seeded
    rows = _q("SELECT name, stock_qty, reorder_point, target_stock FROM products")
    critical = [r for r in rows if r[1] <= r[2]]
    near = [r for r in rows if r[1] == r[2] + 1]
    safe = [r for r in rows if r[1] > r[2] + 1]
    assert len(critical) == 2 and len(near) == 1 and len(safe) == 17
    assert all(r[1] >= 2 * r[2] for r in safe)
    assert all(5 <= r[2] <= 20 and 3 * r[2] <= r[3] <= 5 * r[2] for r in rows)
    assert {c["name"] for c in summary["critical"]} == {r[0] for r in critical}
    assert all(c["channel"] == "telegram" for c in summary["critical"])  # demo: Telegram mesajı


def test_profit_leader_is_powerbank(seeded):
    summary, _ = seeded
    rows = _q(
        "SELECT p.name, p.category, SUM(s.qty * (s.unit_price - p.unit_cost)) AS profit "
        "FROM sales s JOIN products p ON p.id = s.product_id "
        "GROUP BY p.id ORDER BY profit DESC"
    )
    leader, second = rows[0], rows[1]
    assert leader[1] == "powerbank"
    assert leader[2] >= second[2] * Decimal("1.20")
    assert summary["top_profit"][0]["name"] == leader[0]


def test_sales_shape(seeded):
    (lo, hi, online, total) = _q(
        "SELECT MIN(sold_at), MAX(sold_at), "
        "SUM(CASE WHEN channel = 'online' THEN 1 ELSE 0 END), COUNT(*) FROM sales"
    )[0]
    assert lo >= datetime(2026, 4, 1, tzinfo=UTC) and hi < datetime(2026, 9, 14, tzinfo=UTC)
    assert 0.34 <= online / total <= 0.46
    monthly = dict(_q("SELECT to_char(sold_at, 'YYYY-MM'), COUNT(*) FROM sales GROUP BY 1"))
    assert monthly["2026-08"] > monthly["2026-04"] and monthly["2026-08"] > monthly["2026-05"]
    (bad,) = _q("SELECT COUNT(*) FROM sales WHERE total <> ROUND(qty * unit_price, 2)")[0]
    assert bad == 0


def test_fixed_expenses(seeded):
    rows = _q(
        "SELECT category, COUNT(*), MIN(amount), MAX(amount), "
        "BOOL_AND(EXTRACT(DAY FROM spent_at AT TIME ZONE 'Europe/Istanbul') = 1) "
        "FROM expenses WHERE category IN ('kira', 'maas') GROUP BY 1"
    )
    by_cat = {r[0]: r[1:] for r in rows}
    assert by_cat["kira"] == (6, Decimal("25000.00"), Decimal("25000.00"), True)
    assert by_cat["maas"] == (6, Decimal("60000.00"), Decimal("60000.00"), True)
    cats = {r[0] for r in _q("SELECT DISTINCT category FROM expenses")}
    assert cats == {"kira", "maas", "elektrik", "kargo", "reklam", "tedarik"}
