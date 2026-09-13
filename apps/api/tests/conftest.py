"""Test altyapısı: DATABASE_URL'den türetilen ayrı bir test veritabanı (TEST_DB_NAME), schema.sql,
her testte tablolar boşaltılır. Paralel koşan oturumlar TEST_DB_NAME'i farklı vermeli."""

from __future__ import annotations

import os
import pathlib
import re
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import psycopg
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[3]
SCHEMA = ROOT / "docs" / "schema.sql"


def _with_db(url: str, name: str) -> str:
    return re.sub(r"/[^/?]+(\?.*)?$", lambda m: f"/{name}{m.group(1) or ''}", url)


_BASE = os.environ.get("DATABASE_URL", "postgresql://localhost:5432/otohesap")
_NAME = os.environ.get("TEST_DB_NAME", "otohesap_test")
TEST_URL = _with_db(_BASE, _NAME)
ADMIN_URL = _with_db(_BASE, "postgres")

# Uygulama ayarları import edilmeden ÖNCE ortam sabitlenir.
os.environ["DATABASE_URL"] = TEST_URL
os.environ["DATABASE_URL_RO"] = TEST_URL
os.environ["LLM_PROVIDER"] = "fake"
os.environ["AGENT_SCHEDULER_ENABLED"] = "false"
os.environ["NOTIFY_DRY_RUN"] = "true"
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "")


@pytest.fixture(scope="session", autouse=True)
def _database():
    with psycopg.connect(ADMIN_URL, autocommit=True) as conn:
        conn.execute(f'DROP DATABASE IF EXISTS "{_NAME}" WITH (FORCE)')
        conn.execute(f'CREATE DATABASE "{_NAME}"')
    with psycopg.connect(TEST_URL, autocommit=True) as conn:
        conn.execute(SCHEMA.read_text())
    yield


@pytest.fixture
def db():
    from app.db import SessionLocal

    with SessionLocal() as session:
        yield session
        session.rollback()
    from sqlalchemy import text

    from app.db import engine

    with engine.begin() as conn:
        conn.execute(
            text(
                "TRUNCATE sales, expenses, purchase_orders, chat_log, products, suppliers "
                "RESTART IDENTITY CASCADE"
            )
        )


@pytest.fixture
def client(db):
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def small_data(db):
    """Küçük, elle bilinen veri seti: 2 tedarikçi, 3 ürün (1 kritik), 6 satış, 4 gider."""
    from app.models import Expense, Product, Sale, Supplier

    s1 = Supplier(
        name="Kablo A.Ş.", contact_channel="telegram", contact_address="111", lead_time_days=2
    )
    s2 = Supplier(name="Güç Ltd.", contact_channel="email", contact_address="guc@example.com")
    db.add_all([s1, s2])
    db.flush()
    p1 = Product(
        name="USB-C Kablo",
        category="kablo-sarj",
        unit_cost=Decimal("50"),
        sale_price=Decimal("120"),
        stock_qty=40,
        reorder_point=10,
        target_stock=60,
        supplier_id=s1.id,
    )
    p2 = Product(
        name="Powerbank 10000",
        category="powerbank",
        unit_cost=Decimal("400"),
        sale_price=Decimal("900"),
        stock_qty=5,
        reorder_point=8,
        target_stock=30,
        supplier_id=s2.id,
    )  # KRİTİK
    p3 = Product(
        name="Silikon Kılıf",
        category="kilif",
        unit_cost=Decimal("30"),
        sale_price=Decimal("90"),
        stock_qty=25,
        reorder_point=10,
        target_stock=40,
        supplier_id=s1.id,
    )
    db.add_all([p1, p2, p3])
    db.flush()
    now = datetime.now(UTC)
    sales = [
        Sale(
            sold_at=now - timedelta(days=1),
            product_id=p2.id,
            qty=2,
            unit_price=Decimal("900"),
            total=Decimal("1800"),
            channel="magaza",
        ),
        Sale(
            sold_at=now - timedelta(days=2),
            product_id=p1.id,
            qty=5,
            unit_price=Decimal("120"),
            total=Decimal("600"),
            channel="online",
        ),
        Sale(
            sold_at=now - timedelta(days=3),
            product_id=p3.id,
            qty=3,
            unit_price=Decimal("90"),
            total=Decimal("270"),
            channel="magaza",
        ),
        Sale(
            sold_at=now - timedelta(days=40),
            product_id=p2.id,
            qty=1,
            unit_price=Decimal("900"),
            total=Decimal("900"),
            channel="online",
        ),
        Sale(
            sold_at=now - timedelta(days=70),
            product_id=p1.id,
            qty=10,
            unit_price=Decimal("120"),
            total=Decimal("1200"),
            channel="magaza",
        ),
        Sale(
            sold_at=now - timedelta(days=100),
            product_id=p3.id,
            qty=4,
            unit_price=Decimal("90"),
            total=Decimal("360"),
            channel="online",
        ),
    ]
    expenses = [
        Expense(spent_at=now - timedelta(days=1), category="reklam", amount=Decimal("500")),
        Expense(spent_at=now - timedelta(days=5), category="kira", amount=Decimal("3000")),
        Expense(spent_at=now - timedelta(days=45), category="kira", amount=Decimal("3000")),
        Expense(spent_at=now - timedelta(days=80), category="elektrik", amount=Decimal("700")),
    ]
    db.add_all(sales + expenses)
    db.commit()
    return {"suppliers": [s1, s2], "products": [p1, p2, p3], "critical": p2}
