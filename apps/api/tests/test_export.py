"""/api/export/*.csv — BOM, `;` ayraç, Türkçe başlık, ondalık virgül, formül enjeksiyonu."""

from __future__ import annotations

import csv
import io
import re
from datetime import UTC, datetime
from decimal import Decimal

BOM = b"\xef\xbb\xbf"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")
SALES_HEADER = "Tarih;Ürün;Adet;Birim Fiyat;Toplam;Kanal"
EXPENSES_HEADER = "Tarih;Kategori;Tutar;Tedarikçi;Not"


def _text(resp) -> str:
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert "charset=utf-8" in resp.headers["content-type"]
    assert resp.headers["content-disposition"].startswith("attachment; filename=")
    assert resp.content.startswith(BOM)
    text = resp.content[len(BOM) :].decode("utf-8")
    assert text.endswith("\r\n")
    return text


def _lines(resp) -> list[str]:
    return _text(resp)[:-2].split("\r\n")


def _rows(resp) -> list[list[str]]:
    return list(csv.reader(io.StringIO(_text(resp)), delimiter=";"))


def test_sales_csv(client, small_data):
    resp = client.get("/api/export/sales.csv")
    lines = _lines(resp)
    assert 'filename="satislar.csv"' in resp.headers["content-disposition"]
    assert lines[0] == SALES_HEADER
    assert len(lines) == 1 + 6
    oldest = lines[1].split(";")  # -100 gün: Silikon Kılıf x4 online
    assert DATE_RE.match(oldest[0])
    assert oldest[1:] == ["Silikon Kılıf", "4", "90,00", "360,00", "online"]
    newest = lines[-1].split(";")
    assert newest[1:] == ["Powerbank 10000", "2", "900,00", "1800,00", "magaza"]


def test_expenses_csv(client, small_data):
    resp = client.get("/api/export/expenses.csv")
    lines = _lines(resp)
    assert 'filename="giderler.csv"' in resp.headers["content-disposition"]
    assert lines[0] == EXPENSES_HEADER
    assert len(lines) == 1 + 4
    oldest = lines[1].split(";")  # -80 gün: elektrik, tedarikçi/not boş
    assert DATE_RE.match(oldest[0])
    assert oldest[1:] == ["elektrik", "700,00", "", ""]
    assert lines[-1].split(";")[1:3] == ["reklam", "500,00"]


def test_formula_injection_escaped(client, db):
    from app.models import Expense, Product, Sale

    now = datetime.now(UTC)
    p = Product(
        name="@Kablo",
        category="-kablo",
        unit_cost=Decimal("10"),
        sale_price=Decimal("20"),
        stock_qty=5,
        reorder_point=1,
        target_stock=10,
    )
    db.add(p)
    db.flush()
    db.add_all(
        [
            Sale(sold_at=now, product_id=p.id, qty=3, unit_price=20, total=60, channel="magaza"),
            Expense(
                spent_at=now,
                category="reklam",
                amount=Decimal("700"),
                vendor="+Ajans",
                note='=HYPERLINK("http://kotu.example")',
            ),
            Expense(
                spent_at=now, category="kargo", amount=Decimal("15"), vendor="\tSekme", note="-eksi"
            ),
        ]
    )
    db.commit()
    sales = _rows(client.get("/api/export/sales.csv"))
    assert sales[1][1:] == ["'@Kablo", "3", "20,00", "60,00", "magaza"]  # sayılar öneksiz
    expenses = _rows(client.get("/api/export/expenses.csv"))
    by_cat = {r[1]: r for r in expenses[1:]}
    assert by_cat["reklam"][2:] == ["700,00", "'+Ajans", '\'=HYPERLINK("http://kotu.example")']
    assert by_cat["kargo"][2:] == ["15,00", "'\tSekme", "'-eksi"]
    raw = _text(client.get("/api/export/expenses.csv"))
    assert "'=HYPERLINK" in raw and ";=HYPERLINK" not in raw


def test_empty_csv(client):
    assert _lines(client.get("/api/export/sales.csv")) == [SALES_HEADER]
    assert _lines(client.get("/api/export/expenses.csv")) == [EXPENSES_HEADER]
