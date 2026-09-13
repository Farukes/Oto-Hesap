"""services/agent.run_check + POST /api/agent/check + soru bankası dosyasının bütünlüğü."""

from __future__ import annotations

import json
import pathlib
from collections import Counter
from decimal import Decimal

import pytest
import sqlglot
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlglot import exp

from app.config import settings
from app.models import Product, PurchaseOrder
from app.services.agent import (
    OPEN_STATUSES,
    REASON_NO_SUPPLIER,
    REASON_OPEN_ORDER,
    format_try,
    run_check,
)

BANK = pathlib.Path(__file__).resolve().parents[1] / "app" / "data" / "soru_bankasi.json"
ALLOWED_TABLES = {
    "sales",
    "expenses",
    "products",
    "suppliers",
    "purchase_orders",
    "v_monthly_cashflow",
}
DEMO_QUESTIONS = [
    "En çok kazancım hangi üründen?",
    "Bu ay toplam giderim ne kadar?",
    "Son 3 ayda gelir-gider farkı nasıl değişti?",
    "Hangi ürünler kritik stokta?",
    "En çok gider hangi kategoride?",
]


# ---------------------------------------------------------------- run_check


def test_run_check_creates_exactly_one_draft(db, small_data):
    result = run_check(db)

    assert result["created"] == 1
    assert result["skipped"] == []
    (draft,) = result["drafts"]
    critical = small_data["critical"]
    assert draft["product_id"] == critical.id
    assert draft["product_name"] == "Powerbank 10000"
    assert draft["qty"] == 25  # 30 hedef - 5 stok
    assert draft["est_amount"] == 10000.0  # 25 × 400
    assert draft["status"] == "draft"
    assert draft["supplier_name"] == "Güç Ltd." and draft["supplier_channel"] == "email"
    assert draft["sent_at"] is None and draft["created_at"]
    assert set(draft) == {
        "id",
        "created_at",
        "product_id",
        "product_name",
        "supplier_id",
        "supplier_name",
        "supplier_channel",
        "qty",
        "est_amount",
        "status",
        "message_text",
        "sent_at",
        "notify_ref",
    }
    assert draft["notify_ref"] is None

    msg = draft["message_text"]
    assert msg.startswith(f"DEMO · sentetik sipariş #{draft['id']} — Merhaba Güç Ltd., ")
    assert f"{settings.business_name} için sipariş talebi: Powerbank 10000 × 25 adet." in msg
    assert "Tahmini tutar 10.000,00 ₺." in msg
    assert "Teslim süresi 3 gün." in msg
    assert msg.endswith("Onay için bu mesajı yanıtlayabilirsiniz. — OtoHesap")

    rows = db.execute(select(PurchaseOrder)).scalars().all()
    assert len(rows) == 1 and rows[0].est_amount == Decimal("10000.00")


def test_run_check_second_call_is_protected(db, small_data):
    assert run_check(db)["created"] == 1
    second = run_check(db)

    assert second["created"] == 0 and second["drafts"] == []
    assert second["skipped"] == [
        {"product_id": small_data["critical"].id, "reason": REASON_OPEN_ORDER}
    ]
    assert len(db.execute(select(PurchaseOrder)).scalars().all()) == 1


def _manual_draft(db, product) -> PurchaseOrder:
    po = PurchaseOrder(
        product_id=product.id,
        supplier_id=product.supplier_id,
        qty=1,
        est_amount=Decimal("1.00"),
        status="draft",
        message_text="elle",
    )
    db.add(po)
    db.flush()
    return po


def test_manual_draft_blocks_run_check_and_direct_insert_raises(db, small_data):
    critical = small_data["critical"]
    manual = _manual_draft(db, critical)
    db.commit()

    result = run_check(db)
    assert result["created"] == 0 and result["drafts"] == []
    assert result["skipped"] == [{"product_id": critical.id, "reason": REASON_OPEN_ORDER}]
    rows = db.execute(select(PurchaseOrder)).scalars().all()
    assert [r.id for r in rows] == [manual.id]

    # Oturum savepoint sonrası sağlıklı; DB indeksi doğrudan ikinci draft'ı da reddeder
    with pytest.raises(IntegrityError) as ei:
        _manual_draft(db, critical)
    assert "ux_open_order_per_product" in str(ei.value)
    db.rollback()


def test_run_check_continues_after_integrity_error(db, small_data):
    usb, powerbank, _ = small_data["products"]
    usb.stock_qty = usb.reorder_point  # ikinci kritik ürün
    _manual_draft(db, powerbank)  # Powerbank kilitli
    db.commit()

    result = run_check(db)
    assert result["created"] == 1
    assert result["drafts"][0]["product_id"] == usb.id
    assert result["drafts"][0]["qty"] == 50  # 60 hedef - 10 stok
    assert result["skipped"] == [{"product_id": powerbank.id, "reason": REASON_OPEN_ORDER}]
    # id mesajın içinde
    assert (
        f"#{result['drafts'][0]['id']} — Merhaba Kablo A.Ş." in result["drafts"][0]["message_text"]
    )


@pytest.mark.parametrize("status", OPEN_STATUSES)
def test_open_statuses_block_new_draft(db, small_data, status):
    run_check(db)
    order = db.execute(select(PurchaseOrder)).scalar_one()
    order.status = status
    db.commit()
    assert run_check(db)["created"] == 0


def test_rejected_order_is_not_open(db, small_data):
    run_check(db)
    order = db.execute(select(PurchaseOrder)).scalar_one()
    order.status = "rejected"
    db.commit()
    assert run_check(db)["created"] == 1  # reddedilen ürün yeniden taslağa düşer


def test_run_check_skips_product_without_supplier(db, small_data):
    orphan = Product(
        name="Yalnız Ürün",
        category="aksesuar",
        unit_cost=Decimal("10"),
        sale_price=Decimal("20"),
        stock_qty=0,
        reorder_point=5,
        target_stock=10,
        supplier_id=None,
    )
    db.add(orphan)
    db.commit()

    result = run_check(db)
    assert result["created"] == 1  # yalnız Powerbank
    assert result["skipped"] == [{"product_id": orphan.id, "reason": REASON_NO_SUPPLIER}]


def test_run_check_qty_is_at_least_one(db, small_data):
    critical = small_data["critical"]
    critical.target_stock = critical.stock_qty  # hedef = stok → fark 0
    db.commit()
    result = run_check(db)
    assert result["drafts"][0]["qty"] == 1


def test_run_check_no_critical_products(db, small_data):
    critical = small_data["critical"]
    critical.stock_qty = 100
    db.commit()
    assert run_check(db) == {"created": 0, "drafts": [], "skipped": []}


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Decimal("12500"), "12.500,00"),
        (Decimal("10000.00"), "10.000,00"),
        (Decimal("0.5"), "0,50"),
        (Decimal("999.999"), "1.000,00"),
        (Decimal("1234567.891"), "1.234.567,89"),
        (7, "7,00"),
    ],
)
def test_format_try(value, expected):
    assert format_try(value) == expected


# ---------------------------------------------------------------- uç


def test_agent_check_endpoint(client, small_data):
    r = client.post("/api/agent/check")
    assert r.status_code == 200
    body = r.json()
    assert body["created"] == 1 and body["skipped"] == []
    assert body["drafts"][0]["product_name"] == "Powerbank 10000"
    assert body["drafts"][0]["est_amount"] == 10000.0

    r2 = client.post("/api/agent/check")
    assert r2.status_code == 200 and r2.json()["created"] == 0
    assert r2.json()["skipped"] == [
        {"product_id": small_data["critical"].id, "reason": "acik_siparis_var"}
    ]


# ---------------------------------------------------------------- soru bankası (Text-to-SQL)


@pytest.fixture(scope="module")
def bank() -> list[dict]:
    data = json.loads(BANK.read_text(encoding="utf-8"))
    return data["questions"]


def test_bank_shape_and_distribution(bank):
    assert len(bank) == 15
    ids = [q["id"] for q in bank]
    assert ids == [f"Q{i:02d}" for i in range(1, 16)]
    for q in bank:
        assert set(q) - {"demo_order"} == {"id", "question", "sql", "demo", "kind", "expected"}
        assert (
            q["question"].strip() == q["question"]
            and q["question"].endswith("?")
            or (q["kind"] == "saldirgan")
        )
    assert Counter(q["kind"] for q in bank) == {
        "basit": 5,
        "tarih": 3,
        "join": 3,
        "uc": 2,
        "saldirgan": 2,
    }


def test_bank_demo_questions_verbatim(bank):
    demo = [q["question"] for q in bank if q["demo"]]
    assert sorted(demo) == sorted(DEMO_QUESTIONS)
    assert all(q["sql"] for q in bank if q["demo"])


def test_bank_attack_questions_have_no_sql(bank):
    attacks = [q for q in bank if q["kind"] == "saldirgan"]
    assert len(attacks) == 2
    for q in attacks:
        assert q["sql"] is None and q["expected"]["reject"] is True and q["demo"] is False


def test_bank_sql_is_single_select_on_allowed_tables(bank):
    for q in bank:
        if q["sql"] is None:
            continue
        sql = q["sql"]
        assert ";" not in sql and "--" not in sql and "/*" not in sql, q["id"]
        tree = sqlglot.parse_one(sql, read="postgres")
        assert isinstance(tree, exp.Select), q["id"]
        tables = {t.name for t in tree.find_all(exp.Table)}
        assert tables and tables <= ALLOWED_TABLES, (q["id"], tables)
        assert tables == set(q["expected"]["tables"]), q["id"]
        for alias in tree.find_all(exp.Alias):
            assert alias.alias.isascii(), (q["id"], alias.alias)


def test_bank_sql_runs_on_postgres(db, small_data, bank):
    for q in bank:
        if q["sql"] is None:
            continue
        rows = db.execute(text(q["sql"])).fetchall()
        assert isinstance(rows, list), q["id"]
