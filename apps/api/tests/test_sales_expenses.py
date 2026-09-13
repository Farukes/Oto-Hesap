"""Satış ve gider CRUD — stok düşme/iade, yetersiz stok, arama, sayfalama."""

from __future__ import annotations

import pytest


def _stock(client, product_id: int) -> int:
    products = client.get("/api/products").json()
    return next(p["stock_qty"] for p in products if p["id"] == product_id)


@pytest.fixture
def ids(small_data) -> dict[str, int]:
    p1, p2, p3 = small_data["products"]
    return {"kablo": p1.id, "powerbank": p2.id, "kilif": p3.id}


# --- satış ----------------------------------------------------------------------------


def test_create_sale_reduces_stock(client, ids):
    r = client.post("/api/sales", json={"product_id": ids["kablo"], "qty": 5})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["product_name"] == "USB-C Kablo"
    assert body["unit_price"] == 120.0  # ürünün sale_price'ı
    assert body["total"] == 600.0
    assert body["channel"] == "magaza"
    assert body["qty"] == 5 and body["sold_at"]
    assert _stock(client, ids["kablo"]) == 35


def test_create_sale_insufficient_stock(client, ids):
    r = client.post("/api/sales", json={"product_id": ids["powerbank"], "qty": 6})
    assert r.status_code == 400
    assert r.json()["detail"] == "Stok yetersiz: 5 adet var"
    assert _stock(client, ids["powerbank"]) == 5
    assert client.get("/api/sales").json()["total"] == 6


def test_create_sale_makes_product_critical(client, ids):
    # demo: satış ekleyince stok kritiğe düşer (kablo: 40 -> 10, eşik 10)
    r = client.post("/api/sales", json={"product_id": ids["kablo"], "qty": 30})
    assert r.status_code == 201
    product = next(p for p in client.get("/api/products").json() if p["id"] == ids["kablo"])
    assert product["stock_qty"] == 10 and product["is_critical"] is True


def test_create_sale_unknown_product(client, ids):
    r = client.post("/api/sales", json={"product_id": 999, "qty": 1})
    assert r.status_code == 404
    assert r.json()["detail"] == "Ürün bulunamadı"


def test_create_sale_with_price_channel_and_date(client, ids):
    payload = {
        "product_id": ids["kilif"],
        "qty": 2,
        "unit_price": 80,
        "channel": "online",
        "sold_at": "2026-09-01T10:00:00Z",
    }
    body = client.post("/api/sales", json=payload).json()
    assert body["total"] == 160.0 and body["unit_price"] == 80.0
    assert body["channel"] == "online"
    assert body["sold_at"].startswith("2026-09-01T10:00:00")


def test_create_sale_validation(client, ids):
    assert client.post("/api/sales", json={"product_id": ids["kablo"], "qty": 0}).status_code == 422
    r = client.post("/api/sales", json={"product_id": ids["kablo"], "qty": 1, "channel": "tv"})
    assert r.status_code == 422


def test_delete_sale_restores_stock(client, ids):
    sale_id = client.post("/api/sales", json={"product_id": ids["kablo"], "qty": 5}).json()["id"]
    assert _stock(client, ids["kablo"]) == 35
    r = client.delete(f"/api/sales/{sale_id}")
    assert r.status_code == 204 and r.content == b""
    assert _stock(client, ids["kablo"]) == 40
    r = client.delete(f"/api/sales/{sale_id}")
    assert r.status_code == 404 and r.json()["detail"] == "Satış bulunamadı"


def test_update_sale_adjusts_stock_difference(client, ids):
    sale_id = client.post("/api/sales", json={"product_id": ids["kablo"], "qty": 5}).json()["id"]
    assert _stock(client, ids["kablo"]) == 35

    body = client.put(f"/api/sales/{sale_id}", json={"qty": 8}).json()
    assert body["qty"] == 8 and body["total"] == 960.0
    assert _stock(client, ids["kablo"]) == 32

    body = client.put(f"/api/sales/{sale_id}", json={"qty": 2, "unit_price": 100}).json()
    assert body["total"] == 200.0
    assert _stock(client, ids["kablo"]) == 38

    r = client.put(f"/api/sales/{sale_id}", json={"qty": 100})
    assert r.status_code == 400 and r.json()["detail"] == "Stok yetersiz: 38 adet var"
    assert _stock(client, ids["kablo"]) == 38


def test_update_sale_switches_product(client, ids):
    sale_id = client.post("/api/sales", json={"product_id": ids["kablo"], "qty": 5}).json()["id"]
    body = client.put(f"/api/sales/{sale_id}", json={"product_id": ids["kilif"]}).json()
    assert body["product_id"] == ids["kilif"] and body["product_name"] == "Silikon Kılıf"
    assert body["total"] == 450.0  # 5 x yeni ürünün fiyatı (90)
    assert _stock(client, ids["kablo"]) == 40  # iade
    assert _stock(client, ids["kilif"]) == 20  # 25 - 5


def test_update_sale_not_found(client, ids):
    r = client.put("/api/sales/999", json={"qty": 1})
    assert r.status_code == 404 and r.json()["detail"] == "Satış bulunamadı"


def test_list_sales_default_order_and_shape(client, ids):
    body = client.get("/api/sales").json()
    assert body["total"] == 6 and len(body["items"]) == 6
    first = body["items"][0]
    assert first["product_name"] == "Powerbank 10000"  # en yeni satış (1 gün önce)
    assert set(first) == {
        "id",
        "sold_at",
        "product_id",
        "product_name",
        "qty",
        "unit_price",
        "total",
        "channel",
    }
    assert isinstance(first["total"], float)
    dates = [i["sold_at"] for i in body["items"]]
    assert dates == sorted(dates, reverse=True)


def test_list_sales_search_is_case_insensitive(client, ids):
    for q in ("power", "POWER", "bank 100"):
        body = client.get("/api/sales", params={"q": q}).json()
        assert body["total"] == 2, q
        assert all(i["product_name"] == "Powerbank 10000" for i in body["items"])
    assert client.get("/api/sales", params={"q": "yok böyle"}).json() == {"items": [], "total": 0}


def test_list_sales_paging(client, ids):
    page = client.get("/api/sales", params={"limit": 2, "offset": 0}).json()
    assert len(page["items"]) == 2 and page["total"] == 6
    last = client.get("/api/sales", params={"limit": 2, "offset": 5}).json()
    assert len(last["items"]) == 1 and last["total"] == 6
    assert client.get("/api/sales", params={"limit": 0}).status_code == 422
    assert client.get("/api/sales", params={"offset": -1}).status_code == 422


# --- gider ----------------------------------------------------------------------------


def test_create_expense(client, small_data):
    r = client.post(
        "/api/expenses", json={"category": "kargo", "amount": 250.5, "vendor": "Aras Kargo"}
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["amount"] == 250.5 and body["category"] == "kargo"
    assert body["vendor"] == "Aras Kargo" and body["note"] is None and body["spent_at"]
    assert client.get("/api/expenses").json()["total"] == 5


def test_create_expense_validation(client):
    assert client.post("/api/expenses", json={"category": "kira", "amount": 0}).status_code == 422
    assert client.post("/api/expenses", json={"category": "", "amount": 5}).status_code == 422


def test_update_expense(client, small_data):
    expense = client.get("/api/expenses", params={"q": "reklam"}).json()["items"][0]
    body = client.put(
        f"/api/expenses/{expense['id']}", json={"amount": 750, "note": "Instagram"}
    ).json()
    assert body["amount"] == 750.0 and body["note"] == "Instagram"
    assert body["category"] == "reklam"  # dokunulmadı
    body = client.put(f"/api/expenses/{expense['id']}", json={"vendor": None}).json()
    assert body["vendor"] is None and body["amount"] == 750.0
    r = client.put("/api/expenses/999", json={"amount": 1})
    assert r.status_code == 404 and r.json()["detail"] == "Gider bulunamadı"


def test_delete_expense(client, small_data):
    expense = client.get("/api/expenses").json()["items"][0]
    assert client.delete(f"/api/expenses/{expense['id']}").status_code == 204
    assert client.get("/api/expenses").json()["total"] == 3
    r = client.delete(f"/api/expenses/{expense['id']}")
    assert r.status_code == 404 and r.json()["detail"] == "Gider bulunamadı"


def test_list_expenses_search_and_paging(client, small_data):
    client.post(
        "/api/expenses",
        json={"category": "kargo", "amount": 100, "vendor": "Aras Kargo", "note": "iade"},
    )
    assert client.get("/api/expenses", params={"q": "kira"}).json()["total"] == 2
    assert client.get("/api/expenses", params={"q": "KIRA"}).json()["total"] == 2
    assert client.get("/api/expenses", params={"q": "aras"}).json()["total"] == 1  # vendor
    assert client.get("/api/expenses", params={"q": "iade"}).json()["total"] == 1  # note
    body = client.get("/api/expenses", params={"limit": 2, "offset": 3}).json()
    assert body["total"] == 5 and len(body["items"]) == 2
    dates = [i["spent_at"] for i in client.get("/api/expenses").json()["items"]]
    assert dates == sorted(dates, reverse=True)
