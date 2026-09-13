"""Öngörü kartları — kural tabanlı, LLM YOK (docs/research/katalog-3-grup-analiz.md, 9. takım).

En fazla 5 kart, önem sırasına göre (critical > warn > info), Türkçe cümleler, tr-TR sayı biçimi.
Sözcükler (D16): "fark (gelir − gider)" — net kâr değil; "tahmini brüt katkı (birim maliyetle)".
Boş veri -> boş liste. Kurallar:
  1. kritik stok (stock_qty <= reorder_point)                         -> critical
  2. bu ay vs geçen ay fark (gelir − gider) değişimi                   -> warn (düşüş > %10) / info
  3. bu ay vs geçen ay en çok artan gider kategorisi                   -> warn (> %25) / info
  4. son 6 ayın en kârlı ürünü (tahmini brüt katkı, D16)               -> info
  5. online/mağaza kanal payı bu ay vs geçen ay                        -> info
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import SQLColumnExpression, case, func, select
from sqlalchemy.orm import Session

from ..models import Expense, Product, Sale
from ..schemas.analytics import Insight, month_bounds, period_start

MAX_CARDS = 5
NET_DROP_WARN_PCT = 10.0
EXPENSE_RISE_WARN_PCT = 25.0
SEVERITY_ORDER = {"critical": 0, "warn": 1, "info": 2}

CATEGORY_LABELS = {
    "kira": "Kira",
    "maas": "Maaş",
    "elektrik": "Elektrik",
    "kargo": "Kargo",
    "reklam": "Reklam",
    "tedarik": "Tedarik",
}
TR_MONTHS = (
    "Ocak",
    "Şubat",
    "Mart",
    "Nisan",
    "Mayıs",
    "Haziran",
    "Temmuz",
    "Ağustos",
    "Eylül",
    "Ekim",
    "Kasım",
    "Aralık",
)


# ---------------------------------------------------------------- biçimleme (tr-TR)


def fmt_money(value: Decimal | float | int) -> str:
    """4500 -> '4.500 ₺', 1234.5 -> '1.234,50 ₺', -16183.47 -> '-16.183,47 ₺'."""
    q = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    sign = "-" if q < 0 else ""
    q = abs(q)
    whole, frac = divmod(int(q * 100), 100)
    text = f"{whole:,}".replace(",", ".")
    if frac:
        text += f",{frac:02d}"
    return f"{sign}{text} ₺"


def fmt_pct(value: float) -> str:
    """40 -> '%40', 12.34 -> '%12,3' (Türkçe: işaret önde). Mutlak değer beklenir."""
    rounded = round(abs(value), 1)
    text = f"{rounded:.1f}".replace(".", ",")
    if text.endswith(",0"):
        text = text[:-2]
    return f"%{text}"


def pct_change(current: Decimal | float, previous: Decimal | float) -> float | None:
    prev = float(previous)
    if prev == 0:
        return None
    return round((float(current) - prev) / abs(prev) * 100, 1)


def category_label(category: str) -> str:
    return CATEGORY_LABELS.get(category, category.capitalize())


def _month_name(dt: datetime) -> str:
    return TR_MONTHS[dt.month - 1]


# ---------------------------------------------------------------- kurallar


def _critical_stock(db: Session) -> Insight | None:
    rows = db.execute(
        select(Product.name, Product.stock_qty, Product.reorder_point)
        .where(Product.stock_qty <= Product.reorder_point)
        .order_by(Product.stock_qty - Product.reorder_point, Product.id)
    ).all()
    if not rows:
        return None
    n = len(rows)
    shown = ", ".join(f"{r.name} ({r.stock_qty}/{r.reorder_point})" for r in rows[:3])
    if n > 3:
        shown += f" ve {n - 3} ürün daha"
    return Insight(
        id="critical-stock",
        title=f"{n} ürün kritik stokta",
        body=f"{shown} yeniden sipariş eşiğinin altında. "
        "Tedarik ekranından sipariş taslağı oluşturabilirsiniz.",
        severity="critical",
        metric="critical_count",
        change_pct=None,
    )


def _sum_between(
    db: Session,
    column: SQLColumnExpression[datetime],
    value: SQLColumnExpression[Decimal],
    start: datetime,
    end: datetime,
) -> Decimal:
    total = db.execute(
        select(func.coalesce(func.sum(value), 0)).where(column >= start, column < end)
    ).scalar_one()
    return Decimal(total)


def _net_change(db: Session, now: datetime) -> Insight | None:
    prev, this, nxt = month_bounds(now)
    inc_prev = _sum_between(db, Sale.sold_at, Sale.total, prev, this)
    inc_cur = _sum_between(db, Sale.sold_at, Sale.total, this, nxt)
    exp_prev = _sum_between(db, Expense.spent_at, Expense.amount, prev, this)
    exp_cur = _sum_between(db, Expense.spent_at, Expense.amount, this, nxt)
    if inc_prev == exp_prev == 0 and inc_cur == exp_cur == 0:
        return None
    net_prev, net_cur = inc_prev - exp_prev, inc_cur - exp_cur
    change = pct_change(net_cur, net_prev)
    span = f"1–{now.day} {_month_name(this)}"
    detail = f"Bu ay ({span}) {fmt_money(net_cur)}, {_month_name(prev)} {fmt_money(net_prev)}."
    if change is None:
        return Insight(
            id="net-change",
            title=f"Bu ayın farkı (gelir − gider): {fmt_money(net_cur)}",
            body=f"{detail} Geçen ay karşılaştırma için yeterli veri yok.",
            severity="info",
            metric="net",
            change_pct=None,
        )
    direction = "arttı" if change >= 0 else "düştü"
    severity = "warn" if change < -NET_DROP_WARN_PCT else "info"
    return Insight(
        id="net-change",
        title=f"Fark (gelir − gider) geçen aya göre {fmt_pct(change)} {direction}",
        body=detail,
        severity=severity,
        metric="net",
        change_pct=change,
    )


def _expense_rise(db: Session, now: datetime) -> Insight | None:
    prev, this, nxt = month_bounds(now)
    in_prev = func.sum(case((Expense.spent_at < this, Expense.amount), else_=0)).label("prev")
    in_cur = func.sum(case((Expense.spent_at >= this, Expense.amount), else_=0)).label("cur")
    rows = db.execute(
        select(Expense.category, in_prev, in_cur)
        .where(Expense.spent_at >= prev, Expense.spent_at < nxt)
        .group_by(Expense.category)
    ).all()
    risen = [(r.category, Decimal(r.prev), Decimal(r.cur)) for r in rows if r.cur > r.prev]
    if not risen:
        return None
    category, amt_prev, amt_cur = max(risen, key=lambda r: (r[2] - r[1], r[0]))
    change = pct_change(amt_cur, amt_prev)
    label = category_label(category)
    if change is None:
        title = f"{label} gideri bu ay başladı"
        body = f"{label} için geçen ay gider yoktu; bu ay {fmt_money(amt_cur)}."
        severity = "info"
    else:
        title = f"{label} gideri geçen aya göre {fmt_pct(change)} arttı"
        body = (
            f"{label} gideri geçen aya göre {fmt_pct(change)} arttı "
            f"({fmt_money(amt_prev)} → {fmt_money(amt_cur)})."
        )
        severity = "warn" if change > EXPENSE_RISE_WARN_PCT else "info"
    return Insight(
        id="expense-rise",
        title=title,
        body=body,
        severity=severity,
        metric=f"expense:{category}",
        change_pct=change,
    )


def _top_product(db: Session, now: datetime) -> Insight | None:
    start = period_start("half", now)
    profit = func.sum(Sale.qty * (Sale.unit_price - Product.unit_cost)).label("profit")
    row = db.execute(
        select(Product.name, profit, func.sum(Sale.qty).label("qty"))
        .join(Product, Product.id == Sale.product_id)
        .where(Sale.sold_at >= start)
        .group_by(Product.id, Product.name)
        .order_by(profit.desc(), Product.id)
        .limit(1)
    ).first()
    if row is None:
        return None
    return Insight(
        id="top-product",
        title=f"En kârlı ürün (tahmini): {row.name}",
        body=f"Son 6 ayda {fmt_money(row.profit)} tahmini brüt katkı "
        f"(mevcut birim maliyetle), {int(row.qty)} adet satış.",
        severity="info",
        metric="top_product_profit",
        change_pct=None,
    )


def _channel_share(db: Session, now: datetime) -> Insight | None:
    prev, this, nxt = month_bounds(now)
    online = func.sum(case((Sale.channel == "online", Sale.total), else_=0))
    row_prev = db.execute(
        select(online, func.sum(Sale.total)).where(Sale.sold_at >= prev, Sale.sold_at < this)
    ).one()
    row_cur = db.execute(
        select(online, func.sum(Sale.total)).where(Sale.sold_at >= this, Sale.sold_at < nxt)
    ).one()
    if not row_cur[1]:
        return None
    share_cur = float(row_cur[0]) / float(row_cur[1]) * 100
    if not row_prev[1]:
        return Insight(
            id="channel-share",
            title=f"Online kanal payı {fmt_pct(share_cur)}",
            body=f"Bu ay cironun {fmt_pct(share_cur)} kadarı online, kalanı mağaza satışı.",
            severity="info",
            metric="online_share",
            change_pct=None,
        )
    share_prev = float(row_prev[0]) / float(row_prev[1]) * 100
    delta = round(share_cur - share_prev, 1)
    direction = "arttı" if delta >= 0 else "azaldı"
    return Insight(
        id="channel-share",
        title=f"Online kanal payı {fmt_pct(share_prev)} → {fmt_pct(share_cur)}",
        body=f"Ciroda online payı geçen aya göre {fmt_pct(delta)[1:]} puan {direction} "
        f"({fmt_pct(share_prev)} → {fmt_pct(share_cur)}); kalanı mağaza satışı.",
        severity="info",
        metric="online_share",
        change_pct=delta,
    )


def build_insights(db: Session, now: datetime | None = None) -> list[Insight]:
    """Kuralları sırayla değerlendirir; boş veri -> []. Sıralama: critical, warn, info."""
    now = (now or datetime.now(UTC)).astimezone(UTC)
    cards = [
        _critical_stock(db),
        _net_change(db, now),
        _expense_rise(db, now),
        _top_product(db, now),
        _channel_share(db, now),
    ]
    present = [c for c in cards if c is not None]
    present.sort(key=lambda c: SEVERITY_ORDER[c.severity])  # stable: kural sırası korunur
    return present[:MAX_CARDS]
