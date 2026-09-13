"""GET /api/products (is_critical, supplier_name, open_order_id) ve PATCH /api/products/{id}."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.models import PurchaseOrder


def _by_id(client) -> dict[int, dict]:
    r = client.get("/api/products")
    assert r.status_code == 200
    return {p["id"]: p for p in r.json()}


def test_list_products_flags_and_shape(client, small_data):
    p1, p2, p3 = small_data["products"]
    products = _by_id(client)
    assert len(products) == 3
    assert products[p2.id]["is_critical"] is True  # 5 <= 8
    assert products[p1.id]["is_critical"] is False and products[p3.id]["is_critical"] is False
    assert all(p["open_order_id"] is None for p in products.values())
    assert products[p1.id]["supplier_name"] == "Kablo A.Ş."
    assert products[p2.id]["supplier_name"] == "Güç Ltd."
    assert products[p2.id]["unit_cost"] == 400.0 and products[p2.id]["sale_price"] == 900.0
    assert set(products[p1.id]) == {
        "id",
        "name",
        "category",
        "unit_cost",
        "sale_price",
        "stock_qty",
        "reorder_point",
        "target_stock",
        "supplier_id",
        "supplier_name",
        "is_critical",
        "open_order_id",
    }


def test_open_order_id_follows_open_statuses(client, db, small_data):
    """draft/approved/sent → open_order_id; rejected → None. D17: ürün başına tek açık sipariş
    (ux_open_order_per_product), bu yüzden geçişler aynı kayıt üzerinde test edilir."""
    p2 = small_data["critical"]
    s2 = small_data["suppliers"][1]
    now = datetime.now(UTC)

    def order(status: str, minutes_ago: int) -> PurchaseOrder:
        po = PurchaseOrder(
            created_at=now - timedelta(minutes=minutes_ago),
            product_id=p2.id,
            supplier_id=s2.id,
            qty=25,
            est_amount=Decimal("10000"),
            status=status,
        )
        db.add(po)
        db.commit()
        return po

    old_rejected = order("rejected", 60)  # eski, kapalı: sayılmaz
    assert _by_id(client)[p2.id]["open_order_id"] is None

    draft = order("draft", 30)
    assert _by_id(client)[p2.id]["open_order_id"] == draft.id

    order("rejected", 10)  # daha yeni ama açık değil
    assert _by_id(client)[p2.id]["open_order_id"] == draft.id

    for status in ("approved", "sent"):
        draft.status = status
        db.commit()
        assert _by_id(client)[p2.id]["open_order_id"] == draft.id, status

    draft.status = "rejected"
    db.commit()
    assert _by_id(client)[p2.id]["open_order_id"] is None

    others = [p for pid, p in _by_id(client).items() if pid != p2.id]
    assert all(p["open_order_id"] is None for p in others)
    assert old_rejected.id != draft.id


def test_patch_product(client, small_data):
    p1 = small_data["products"][0]
    body = client.patch(f"/api/products/{p1.id}", json={"reorder_point": 45}).json()
    assert body["reorder_point"] == 45 and body["is_critical"] is True  # 40 <= 45

    body = client.patch(
        f"/api/products/{p1.id}", json={"stock_qty": 100, "target_stock": 150}
    ).json()
    assert body["stock_qty"] == 100 and body["target_stock"] == 150
    assert body["is_critical"] is False and body["reorder_point"] == 45
    assert body["supplier_name"] == "Kablo A.Ş."

    assert client.patch(f"/api/products/{p1.id}", json={}).status_code == 200


def test_patch_product_validation_and_404(client, small_data):
    p1 = small_data["products"][0]
    assert client.patch(f"/api/products/{p1.id}", json={"stock_qty": -1}).status_code == 422
    assert client.patch(f"/api/products/{p1.id}", json={"reorder_point": -5}).status_code == 422
    r = client.patch("/api/products/999", json={"stock_qty": 1})
    assert r.status_code == 404 and r.json()["detail"] == "Ürün bulunamadı"
