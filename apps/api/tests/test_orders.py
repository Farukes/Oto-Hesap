"""/api/orders uçları: liste + durum filtresi, tekil, approve (dry-run → sent; tekrar → 409;
NotifyError → approved + 502; yeniden deneme), reject, 404."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.models import PurchaseOrder
from app.services import notify
from app.services.agent import run_check

ORDER_KEYS = {
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


@pytest.fixture
def draft(db, small_data) -> PurchaseOrder:
    run_check(db)
    return db.execute(select(PurchaseOrder)).scalar_one()


def _add_order(db, small_data, *, product, status: str, days_ago: int) -> PurchaseOrder:
    po = PurchaseOrder(
        created_at=datetime.now(UTC) - timedelta(days=days_ago),
        product_id=product.id,
        supplier_id=product.supplier_id,
        qty=3,
        est_amount=Decimal("150.00"),
        status=status,
        message_text="test",
    )
    db.add(po)
    db.commit()
    return po


# ---------------------------------------------------------------- liste / tekil


def test_list_orders_and_filters(client, db, small_data, draft):
    p1 = small_data["products"][0]
    old_sent = _add_order(db, small_data, product=p1, status="sent", days_ago=5)
    rejected = _add_order(db, small_data, product=p1, status="rejected", days_ago=2)

    r = client.get("/api/orders")
    assert r.status_code == 200
    items = r.json()
    assert [i["id"] for i in items] == [draft.id, rejected.id, old_sent.id]  # yeni → eski
    assert set(items[0]) == ORDER_KEYS
    assert items[0]["est_amount"] == 10000.0 and isinstance(items[0]["est_amount"], float)
    assert items[0]["supplier_channel"] == "email"

    assert [i["id"] for i in client.get("/api/orders", params={"status": "draft"}).json()] == [
        draft.id
    ]
    assert [i["id"] for i in client.get("/api/orders", params={"status": "sent"}).json()] == [
        old_sent.id
    ]
    assert client.get("/api/orders", params={"status": "approved"}).json() == []
    assert client.get("/api/orders", params={"status": "bilinmiyor"}).status_code == 422


def test_list_orders_empty(client, db):
    assert client.get("/api/orders").json() == []


def test_get_order(client, draft):
    r = client.get(f"/api/orders/{draft.id}")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == draft.id and body["product_name"] == "Powerbank 10000"
    assert body["status"] == "draft" and body["sent_at"] is None
    assert body["notify_ref"] is None


def test_get_order_404(client, db):
    r = client.get("/api/orders/999")
    assert r.status_code == 404 and r.json()["detail"] == "Sipariş bulunamadı"


# ---------------------------------------------------------------- approve


def test_approve_draft_dry_run_sends(client, db, draft):
    r = client.post(f"/api/orders/{draft.id}/approve")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "sent" and body["sent_at"] is not None
    assert body["notify"] == {"ok": True, "dry_run": True, "channel": "email", "message_id": None}
    assert body["notify_ref"] == "dry-run"
    assert ORDER_KEYS <= set(body)

    db.expire_all()
    row = db.get(PurchaseOrder, draft.id)
    assert row.status == "sent" and row.sent_at is not None
    assert row.sent_at.tzinfo is not None
    assert row.notify_ref == "dry-run"


def test_approve_twice_is_conflict(client, draft):
    assert client.post(f"/api/orders/{draft.id}/approve").status_code == 200
    r = client.post(f"/api/orders/{draft.id}/approve")
    assert r.status_code == 409
    assert r.json()["detail"] == "Sipariş zaten sent durumunda."


def test_approve_notify_error_keeps_approved_then_retry(client, db, draft, monkeypatch):
    def boom(supplier, text):
        raise notify.NotifyError("Telegram HTTP 502: bad gateway")

    monkeypatch.setattr(notify, "send_message", boom)
    r = client.post(f"/api/orders/{draft.id}/approve")
    assert r.status_code == 502
    assert r.json()["detail"] == "Mesaj gönderilemedi; sipariş onaylı bekliyor, tekrar deneyin."

    db.expire_all()
    row = db.get(PurchaseOrder, draft.id)
    assert row.status == "approved" and row.sent_at is None and row.notify_ref is None
    assert client.get(f"/api/orders/{draft.id}").json()["status"] == "approved"

    # tekrar dene: approved → approve yeniden gönderir
    monkeypatch.undo()
    r2 = client.post(f"/api/orders/{draft.id}/approve")
    assert r2.status_code == 200 and r2.json()["status"] == "sent"
    assert r2.json()["notify"]["dry_run"] is True and r2.json()["notify_ref"] == "dry-run"


def test_approve_passes_supplier_and_message(client, draft, monkeypatch):
    seen = {}

    def fake(supplier, text):
        seen["supplier"] = supplier.name
        seen["text"] = text
        return {"ok": True, "dry_run": False, "channel": "telegram", "message_id": 7}

    monkeypatch.setattr(notify, "send_message", fake)
    r = client.post(f"/api/orders/{draft.id}/approve")
    assert r.status_code == 200
    assert seen == {"supplier": "Güç Ltd.", "text": draft.message_text}
    assert r.json()["notify"] == {
        "ok": True,
        "dry_run": False,
        "channel": "telegram",
        "message_id": 7,
    }
    assert r.json()["notify_ref"] == "7"


def test_approve_404(client, db):
    assert client.post("/api/orders/999/approve").status_code == 404


# ---------------------------------------------------------------- reject


def test_reject_draft(client, db, draft):
    r = client.post(f"/api/orders/{draft.id}/reject")
    assert r.status_code == 200
    assert r.json()["status"] == "rejected" and r.json()["sent_at"] is None

    r2 = client.post(f"/api/orders/{draft.id}/reject")
    assert r2.status_code == 409 and r2.json()["detail"] == "Sipariş zaten rejected durumunda."
    r3 = client.post(f"/api/orders/{draft.id}/approve")
    assert r3.status_code == 409 and r3.json()["detail"] == "Sipariş zaten rejected durumunda."


def test_reject_approved(client, db, draft):
    draft.status = "approved"
    db.commit()
    r = client.post(f"/api/orders/{draft.id}/reject")
    assert r.status_code == 200 and r.json()["status"] == "rejected"


def test_reject_sent_is_conflict(client, db, draft):
    assert client.post(f"/api/orders/{draft.id}/approve").status_code == 200
    r = client.post(f"/api/orders/{draft.id}/reject")
    assert r.status_code == 409 and r.json()["detail"] == "Sipariş zaten sent durumunda."


def test_reject_404(client, db):
    r = client.post("/api/orders/999/reject")
    assert r.status_code == 404 and r.json()["detail"] == "Sipariş bulunamadı"
