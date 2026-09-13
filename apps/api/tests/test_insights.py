"""/api/insights ve services/insights — kural tabanlı Öngörü kartları (sözcükler D16)."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from app.services.insights import (
    SEVERITY_ORDER,
    build_insights,
    fmt_money,
    fmt_pct,
    pct_change,
)


def test_formatting():
    assert fmt_money(4500) == "4.500 ₺"
    assert fmt_money(Decimal("1234.5")) == "1.234,50 ₺"
    assert fmt_money(-16183.47) == "-16.183,47 ₺"
    assert fmt_money(0) == "0 ₺"
    assert fmt_pct(40) == "%40"
    assert fmt_pct(12.34) == "%12,3"
    assert fmt_pct(-7.5) == "%7,5"
    assert pct_change(6300, 4500) == 40.0
    assert pct_change(1, 0) is None


def test_insights_small_data(client, small_data):
    r = client.get("/api/insights")
    assert r.status_code == 200
    cards = r.json()
    assert 1 <= len(cards) <= 5
    assert len({c["id"] for c in cards}) == len(cards)
    ranks = [SEVERITY_ORDER[c["severity"]] for c in cards]
    assert ranks == sorted(ranks)
    first = cards[0]
    assert first["id"] == "critical-stock" and first["severity"] == "critical"
    assert first["title"] == "1 ürün kritik stokta"
    assert "Powerbank 10000 (5/8)" in first["body"]
    assert first["metric"] == "critical_count" and first["change_pct"] is None
    by_id = {c["id"]: c for c in cards}
    top = by_id["top-product"]
    assert top["title"] == "En kârlı ürün (tahmini): Powerbank 10000"
    assert "1.500 ₺ tahmini brüt katkı (mevcut birim maliyetle)" in top["body"]
    assert set(cards[0]) == {"id", "title", "body", "severity", "metric", "change_pct"}
    for c in cards:  # D16: "net kâr" denmez
        assert "net kâr" not in (c["title"] + c["body"]).lower()


def test_insights_empty_db(client):
    r = client.get("/api/insights")
    assert r.status_code == 200 and r.json() == []


def test_expense_rise_and_net_rules(db):
    from app.models import Expense

    now = datetime(2026, 9, 13, 12, 0, tzinfo=UTC)
    db.add_all(
        [
            Expense(spent_at=datetime(2026, 8, 5, tzinfo=UTC), category="reklam", amount=4500),
            Expense(spent_at=datetime(2026, 9, 3, tzinfo=UTC), category="reklam", amount=6300),
            Expense(spent_at=datetime(2026, 8, 1, tzinfo=UTC), category="kira", amount=25000),
            Expense(spent_at=datetime(2026, 9, 1, tzinfo=UTC), category="kira", amount=25000),
        ]
    )
    db.commit()
    cards = {c.id: c for c in build_insights(db, now=now)}
    rise = cards["expense-rise"]
    assert rise.severity == "warn" and rise.change_pct == 40.0
    assert rise.body == "Reklam gideri geçen aya göre %40 arttı (4.500 ₺ → 6.300 ₺)."
    assert rise.metric == "expense:reklam"
    net = cards["net-change"]  # -29.500 -> -31.300: %6,1 düşüş, eşik altı -> info
    assert net.severity == "info" and net.change_pct == -6.1
    assert net.title == "Fark (gelir − gider) geçen aya göre %6,1 düştü"
    assert net.body == "Bu ay (1–13 Eylül) -31.300 ₺, Ağustos -29.500 ₺."
    assert "top-product" not in cards and "channel-share" not in cards
