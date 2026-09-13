"""OtoHesap sentetik veri üreticisi — teknoloji aksesuar mağazası, Nisan–Eylül 2026.

Kullanım:
    python data/seed.py --reset [--url postgresql://...]

Bağlantı sırası: --url > DATABASE_URL ortam değişkeni > depo kökündeki .env dosyası.
Şema uygulanmış olmalı: psql "$DATABASE_URL" -f docs/schema.sql

Deterministik: numpy.random.default_rng(42) + Faker.seed(42). İki koşu aynı rakamları verir.
SQLAlchemy'ye bağımlı değildir; psycopg ile doğrudan yazar (COPY ile toplu ekleme).
"""

from __future__ import annotations

import argparse
import calendar
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any

import numpy as np
import psycopg
from faker import Faker

SEED = 42
ROOT = Path(__file__).resolve().parents[1]
TR = timezone(timedelta(hours=3))  # mağaza saati; DB'ye UTC yazılır

DATE_FROM = date(2026, 4, 1)
DATE_TO = date(2026, 9, 13)  # dahil
TARGET_SALES = 600

CATEGORIES = ("kulaklik", "kilif", "kablo-sarj", "powerbank", "aksesuar")

# Demoda rol alan ürünler (adla seçilir; sıralamaya bağlı değil)
PROFIT_LEADER = "Powerbank 20000 mAh"  # kâr sıralamasında tek net kazanan
CRITICAL_PRODUCTS = (PROFIT_LEADER, "Kablosuz Şarjlı Powerbank")  # tam 2 kritik, ikisi de Telegram
NEAR_CRITICAL_PRODUCT = "USB-C Şarj Kablosu 1 m"  # eşiğin 1 üstünde
PROFIT_GAP = 0.20  # lider ile ikinci arasındaki en az fark

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


@dataclass(frozen=True)
class SupplierSpec:
    name: str
    channel: str
    address: str | None  # None -> Faker e-posta
    lead_time_days: int


@dataclass(frozen=True)
class ProductSpec:
    name: str
    category: str
    unit_cost: Decimal
    markup: Decimal  # maliyet üstü marj (0.25–0.60)
    weight: float  # satış popülerliği (göreli)


# 5 tedarikçi; ilki Telegram (chat_id yer tutucu, Ömer gerçek id'yi .env/DB'de günceller)
SUPPLIERS: tuple[SupplierSpec, ...] = (
    SupplierSpec("Anadolu Güç Sistemleri", "telegram", "TELEGRAM_CHAT_ID", 3),
    SupplierSpec("İstanbul Teknoloji İthalat", "email", None, 5),
    SupplierSpec("Marmara Aksesuar Dağıtım", "email", None, 4),
    SupplierSpec("Ege Kablo Sanayi", "email", None, 2),
    SupplierSpec("Karadeniz Elektronik Toptan", "email", None, 7),
)

# Kategori -> tedarikçi (SUPPLIERS sırasına göre indeks)
CATEGORY_SUPPLIER = {
    "powerbank": 0,  # Telegram kanallı tedarikçi
    "kulaklik": 1,
    "kilif": 2,
    "kablo-sarj": 3,
    "aksesuar": 4,
}

D = Decimal
PRODUCTS: tuple[ProductSpec, ...] = (
    # kulaklik
    ProductSpec("Kablosuz Kulaklık Pro", "kulaklik", D("1500"), D("0.45"), 5),
    ProductSpec("Bluetooth Kulak İçi Kulaklık", "kulaklik", D("700"), D("0.55"), 8),
    ProductSpec("Oyuncu Kulaklığı RGB", "kulaklik", D("1300"), D("0.40"), 5),
    ProductSpec("Spor Kulaklık Su Geçirmez", "kulaklik", D("900"), D("0.50"), 5),
    # kilif
    ProductSpec("Silikon Telefon Kılıfı", "kilif", D("60"), D("0.60"), 7),
    ProductSpec("Deri Cüzdan Kılıf", "kilif", D("250"), D("0.55"), 3),
    ProductSpec("Şeffaf Darbe Emici Kılıf", "kilif", D("80"), D("0.60"), 6),
    ProductSpec("Tablet Kılıfı 10 inç", "kilif", D("300"), D("0.50"), 2),
    # kablo-sarj
    ProductSpec("USB-C Şarj Kablosu 1 m", "kablo-sarj", D("70"), D("0.60"), 8),
    ProductSpec("Lightning Kablo 2 m", "kablo-sarj", D("120"), D("0.55"), 5),
    ProductSpec("65 W GaN Hızlı Şarj Adaptörü", "kablo-sarj", D("700"), D("0.45"), 5),
    ProductSpec("Araç İçi Şarj Cihazı", "kablo-sarj", D("200"), D("0.50"), 4),
    # powerbank
    ProductSpec("Powerbank 20000 mAh", "powerbank", D("1100"), D("0.55"), 14),
    ProductSpec("Powerbank 10000 mAh", "powerbank", D("600"), D("0.45"), 6),
    ProductSpec("Mini Powerbank 5000 mAh", "powerbank", D("320"), D("0.40"), 3),
    ProductSpec("Kablosuz Şarjlı Powerbank", "powerbank", D("1400"), D("0.35"), 4),
    # aksesuar
    ProductSpec("Araç İçi Telefon Tutucu", "aksesuar", D("160"), D("0.55"), 4),
    ProductSpec("Temperli Ekran Koruyucu", "aksesuar", D("40"), D("0.60"), 6),
    ProductSpec("Alüminyum Laptop Standı", "aksesuar", D("500"), D("0.45"), 3),
    ProductSpec("Mini Bluetooth Hoparlör", "aksesuar", D("1000"), D("0.40"), 5),
)

# Satış yoğunluğu: ay çarpanı (Ağustos–Eylül belirgin artış) ve gün çarpanı (hafta içi yoğun)
MONTH_FACTOR = {4: 0.80, 5: 0.90, 6: 0.95, 7: 1.00, 8: 1.35, 9: 1.55}
WEEKDAY_FACTOR = (1.2, 1.2, 1.2, 1.2, 1.2, 0.8, 0.5)  # Pzt..Paz
ONLINE_SHARE = 0.40
# Adet dağılımı fiyat bandına göre: pahalı ürün tek-çift, ucuz ürün toplu alınır
QTY_BANDS: tuple[tuple[Decimal, tuple[int, ...], tuple[float, ...]], ...] = (
    (D("800"), (1, 2, 3, 4, 5), (0.50, 0.25, 0.13, 0.08, 0.04)),
    (D("200"), (1, 2, 3, 4, 5, 6), (0.40, 0.26, 0.15, 0.09, 0.06, 0.04)),
    (D("0"), (1, 2, 3, 4, 5, 6, 8, 10), (0.30, 0.24, 0.15, 0.10, 0.08, 0.06, 0.04, 0.03)),
)

# Gider parametreleri
RENT = D("25000.00")
SALARY = D("60000.00")
ELECTRICITY = {4: 2900, 5: 3100, 6: 3800, 7: 5200, 8: 5600, 9: 4100}
DAILY_RATE = {"kargo": 0.85, "reklam": 0.35, "tedarik": 0.28}
SEP_AD_BOOST = 3.2  # Eylül "okula dönüş" kampanyası: reklam sıklığı ve tutarı artar

TRUNCATE_SQL = (
    "TRUNCATE sales, expenses, purchase_orders, chat_log, products, suppliers "
    "RESTART IDENTITY CASCADE"
)


def q2(x: Decimal | float | int) -> Decimal:
    return Decimal(x).quantize(D("0.01"), rounding=ROUND_HALF_UP)


def _days() -> list[date]:
    out, d = [], DATE_FROM
    while d <= DATE_TO:
        out.append(d)
        d += timedelta(days=1)
    return out


def _to_utc(d: date, hour: int, minute: int) -> datetime:
    return datetime(d.year, d.month, d.day, hour, minute, tzinfo=TR).astimezone(UTC)


def _read_env_url() -> str | None:
    env = ROOT / ".env"
    if not env.exists():
        return None
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        if key.strip() == "DATABASE_URL":
            return val.strip().strip("'\"") or None
    return None


def resolve_url(cli_url: str | None) -> str:
    url = cli_url or os.environ.get("DATABASE_URL") or _read_env_url()
    if not url:
        raise SystemExit("DATABASE_URL bulunamadı: --url ver, ortam değişkeni ya da .env ayarla.")
    return url


# ---------------------------------------------------------------- üretim


def _gen_suppliers(fake: Faker) -> list[tuple[str, str, str, int]]:
    rows = []
    for s in SUPPLIERS:
        address = s.address if s.address is not None else fake.company_email()
        rows.append((s.name, s.channel, address, s.lead_time_days))
    return rows


def _gen_products(rng: np.random.Generator) -> list[dict[str, Any]]:
    rows = []
    for spec in PRODUCTS:
        reorder = int(rng.integers(5, 21))
        target = reorder * int(rng.integers(3, 6))
        rows.append(
            {
                "name": spec.name,
                "category": spec.category,
                "unit_cost": q2(spec.unit_cost),
                "sale_price": q2(spec.unit_cost * (1 + spec.markup)),
                "reorder_point": reorder,
                "target_stock": target,
                "supplier_idx": CATEGORY_SUPPLIER[spec.category],
                "weight": spec.weight,
                "stock_qty": 0,  # satışlardan sonra deterministik ayarlanır
            }
        )
    return rows


def _gen_sales(rng: np.random.Generator, products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    days = _days()
    weights = np.array([MONTH_FACTOR[d.month] * WEEKDAY_FACTOR[d.weekday()] for d in days])
    lam = weights / weights.sum() * TARGET_SALES
    pw = np.array([p["weight"] for p in products], dtype=float)
    pw /= pw.sum()
    sales: list[dict[str, Any]] = []
    for d, lam_d in zip(days, lam, strict=True):
        n = int(rng.poisson(lam_d))
        for _ in range(n):
            idx = int(rng.choice(len(products), p=pw))
            sales.append(_one_sale(rng, d, idx, products[idx]))
    sales.sort(key=lambda s: s["sold_at"])
    return sales


def _one_sale(
    rng: np.random.Generator, d: date, idx: int, product: dict[str, Any]
) -> dict[str, Any]:
    online = bool(rng.random() < ONLINE_SHARE)
    hour = int(rng.integers(8, 24)) if online else int(rng.integers(9, 22))
    minute = int(rng.integers(0, 60))
    values, probs = next((v, p) for floor, v, p in QTY_BANDS if product["sale_price"] >= floor)
    qty = int(rng.choice(values, p=probs))
    unit_price = q2(product["sale_price"] * (1 + D(str(round(rng.uniform(-0.05, 0.05), 4)))))
    return {
        "sold_at": _to_utc(d, hour, minute),
        "product_idx": idx,
        "qty": qty,
        "unit_price": unit_price,
        "total": q2(unit_price * qty),
        "channel": "online" if online else "magaza",
    }


def _profit_by_product(
    sales: list[dict[str, Any]], products: list[dict[str, Any]]
) -> list[Decimal]:
    totals = [D("0")] * len(products)
    for s in sales:
        p = products[s["product_idx"]]
        totals[s["product_idx"]] += s["qty"] * (s["unit_price"] - p["unit_cost"])
    return totals


def _ensure_profit_leader(
    rng: np.random.Generator, sales: list[dict[str, Any]], products: list[dict[str, Any]]
) -> int:
    """Lider ürün ikinciden en az PROFIT_GAP kadar önde değilse Ağustos–Eylül'e lider satışı ekler.

    Sabit tohumla normalde tetiklenmez; parametre oynanırsa güvence. Eklenen satır sayısını döner.
    """
    leader = next(i for i, p in enumerate(products) if p["name"] == PROFIT_LEADER)
    added = 0
    while True:
        profit = _profit_by_product(sales, products)
        second = max(v for i, v in enumerate(profit) if i != leader)
        if profit[leader] >= second * (1 + D(str(PROFIT_GAP))):
            break
        d = date(2026, 8, 1) + timedelta(days=int(rng.integers(0, 44)))
        sales.append(_one_sale(rng, d, leader, products[leader]))
        added += 1
    if added:
        sales.sort(key=lambda s: s["sold_at"])
    return added


def _set_stock(rng: np.random.Generator, products: list[dict[str, Any]]) -> None:
    """Tam 2 kritik (stok <= eşik), tam 1 eşiğin 1 üstünde, diğerleri >= 2x eşik."""
    for p in products:
        rp = p["reorder_point"]
        if p["name"] in CRITICAL_PRODUCTS:
            p["stock_qty"] = max(1, rp // 3)
        elif p["name"] == NEAR_CRITICAL_PRODUCT:
            p["stock_qty"] = rp + 1
        else:
            p["stock_qty"] = rp * int(rng.integers(2, 5)) + int(rng.integers(0, 6))


def _gen_expenses(
    rng: np.random.Generator,
    fake: Faker,
    products: list[dict[str, Any]],
    suppliers: list[tuple[str, str, str, int]],
) -> list[tuple[datetime, str, Decimal, str | None, str | None]]:
    rows: list[tuple[datetime, str, Decimal, str | None, str | None]] = []
    months = sorted({(d.year, d.month) for d in _days()})
    cargo_vendors = [f"{fake.last_name()} Lojistik" for _ in range(2)]
    ad_vendors = [f"{fake.last_name()} Dijital Ajans", "Pazar Yeri Vitrin Reklamı"]
    landlord = fake.name()
    utility = "Elektrik Dağıtım A.Ş."

    for year, month in months:
        first = _to_utc(date(year, month, 1), 9, 0)
        mname = TR_MONTHS[month - 1]
        rows.append((first, "kira", RENT, landlord, f"{mname} kirası"))
        rows.append((first, "maas", SALARY, None, f"{mname} maaşları (3 personel)"))
        last_day = calendar.monthrange(year, month)[1]
        bill_day = min(10, last_day)
        if date(year, month, bill_day) <= DATE_TO:
            amt = q2(ELECTRICITY[month] + float(rng.uniform(-250, 250)))
            rows.append(
                (
                    _to_utc(date(year, month, bill_day), 11, 30),
                    "elektrik",
                    amt,
                    utility,
                    f"{mname} faturası",
                )
            )

    for d in _days():
        wd = d.weekday() < 5
        # kargo: hafta içi daha sık; tutar gönderi sayısına göre
        n = int(rng.poisson(DAILY_RATE["kargo"] * (1.2 if wd else 0.5)))
        for _ in range(n):
            amt = q2(float(rng.uniform(150, 900)))
            vendor = cargo_vendors[int(rng.integers(0, len(cargo_vendors)))]
            note = f"Gönderi {fake.bothify('??-#####').upper()}"
            rows.append(
                (
                    _to_utc(d, int(rng.integers(10, 19)), int(rng.integers(0, 60))),
                    "kargo",
                    amt,
                    vendor,
                    note,
                )
            )
        # reklam: Eylül kampanyası
        boost = SEP_AD_BOOST if d.month == 9 else (1.3 if d.month == 8 else 1.0)
        n = int(rng.poisson(DAILY_RATE["reklam"] * boost))
        for _ in range(n):
            amt = q2(float(rng.uniform(600, 2400)) * (1.8 if d.month == 9 else 1.0))
            vendor = ad_vendors[int(rng.integers(0, len(ad_vendors)))]
            note = (
                "Okula dönüş kampanyası"
                if d.month == 9
                else f"{TR_MONTHS[d.month - 1]} sosyal medya reklamı"
            )
            rows.append(
                (
                    _to_utc(d, int(rng.integers(9, 18)), int(rng.integers(0, 60))),
                    "reklam",
                    amt,
                    vendor,
                    note,
                )
            )
        # tedarik: bir ürünün tedarikçisinden parti alımı (adet x maliyet)
        n = int(rng.poisson(DAILY_RATE["tedarik"] * (1.0 if wd else 0.3)))
        for _ in range(n):
            p = products[int(rng.integers(0, len(products)))]
            lot = (4, 13) if p["unit_cost"] >= 300 else (10, 31)
            units = int(rng.integers(*lot))
            amt = q2(p["unit_cost"] * units)
            vendor = suppliers[p["supplier_idx"]][0]
            note = f"{p['name']} x{units}, fatura {fake.bothify('FTR-2026-#####')}"
            rows.append(
                (
                    _to_utc(d, int(rng.integers(9, 18)), int(rng.integers(0, 60))),
                    "tedarik",
                    amt,
                    vendor,
                    note,
                )
            )

    rows.sort(key=lambda r: r[0])
    return rows


# ---------------------------------------------------------------- yazma


def _write(
    conn: psycopg.Connection,
    reset: bool,
    suppliers: list[tuple[str, str, str, int]],
    products: list[dict[str, Any]],
    sales: list[dict[str, Any]],
    expenses: list[tuple[datetime, str, Decimal, str | None, str | None]],
) -> None:
    with conn.cursor() as cur:
        if reset:
            cur.execute(TRUNCATE_SQL)
        supplier_ids: list[int] = []
        for row in suppliers:
            cur.execute(
                "INSERT INTO suppliers (name, contact_channel, contact_address, lead_time_days) "
                "VALUES (%s, %s, %s, %s) RETURNING id",
                row,
            )
            supplier_ids.append(cur.fetchone()[0])  # type: ignore[index]
        product_ids: list[int] = []
        for p in products:
            cur.execute(
                "INSERT INTO products (name, category, unit_cost, sale_price, stock_qty, "
                "reorder_point, target_stock, supplier_id) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
                (
                    p["name"],
                    p["category"],
                    p["unit_cost"],
                    p["sale_price"],
                    p["stock_qty"],
                    p["reorder_point"],
                    p["target_stock"],
                    supplier_ids[p["supplier_idx"]],
                ),
            )
            product_ids.append(cur.fetchone()[0])  # type: ignore[index]
        with cur.copy(
            "COPY sales (sold_at, product_id, qty, unit_price, total, channel) FROM STDIN"
        ) as copy:
            for s in sales:
                copy.write_row(
                    (
                        s["sold_at"],
                        product_ids[s["product_idx"]],
                        s["qty"],
                        s["unit_price"],
                        s["total"],
                        s["channel"],
                    )
                )
        with cur.copy(
            "COPY expenses (spent_at, category, amount, vendor, note) FROM STDIN"
        ) as copy:
            for row in expenses:
                copy.write_row(row)


def _summary(conn: psycopg.Connection) -> dict[str, Any]:
    with conn.cursor() as cur:
        cur.execute("SELECT COALESCE(SUM(total), 0), COUNT(*), MAX(sold_at) FROM sales")
        income, sales_rows, last_sale = cur.fetchone()  # type: ignore[misc]
        cur.execute("SELECT COALESCE(SUM(amount), 0), COUNT(*) FROM expenses")
        expense, expense_rows = cur.fetchone()  # type: ignore[misc]
        cur.execute("SELECT COUNT(*) FROM products")
        n_products = cur.fetchone()[0]  # type: ignore[index]
        cur.execute("SELECT COUNT(*) FROM suppliers")
        n_suppliers = cur.fetchone()[0]  # type: ignore[index]
        cur.execute(
            "SELECT p.id, p.name, p.stock_qty, p.reorder_point, p.target_stock, s.name, "
            "s.contact_channel FROM products p LEFT JOIN suppliers s ON s.id = p.supplier_id "
            "WHERE p.stock_qty <= p.reorder_point ORDER BY p.id"
        )
        critical = [
            {
                "id": r[0],
                "name": r[1],
                "stock_qty": r[2],
                "reorder_point": r[3],
                "target_stock": r[4],
                "supplier": r[5],
                "channel": r[6],
            }
            for r in cur.fetchall()
        ]
        cur.execute(
            "SELECT id, name, stock_qty, reorder_point FROM products "
            "WHERE stock_qty = reorder_point + 1 ORDER BY id"
        )
        near = [
            {"id": r[0], "name": r[1], "stock_qty": r[2], "reorder_point": r[3]}
            for r in cur.fetchall()
        ]
        cur.execute(
            "SELECT p.id, p.name, SUM(s.qty * (s.unit_price - p.unit_cost)) AS profit, "
            "SUM(s.total) AS revenue, SUM(s.qty) AS qty "
            "FROM sales s JOIN products p ON p.id = s.product_id "
            "GROUP BY p.id, p.name ORDER BY profit DESC, p.id LIMIT 3"
        )
        top = [
            {
                "id": r[0],
                "name": r[1],
                "profit": float(r[2]),
                "revenue": float(r[3]),
                "qty": int(r[4]),
            }
            for r in cur.fetchall()
        ]
        cur.execute("SELECT month, income, expense, net FROM v_monthly_cashflow ORDER BY month")
        monthly = [
            {
                "month": r[0].strftime("%Y-%m"),
                "income": float(r[1]),
                "expense": float(r[2]),
                "net": float(r[3]),
            }
            for r in cur.fetchall()
        ]
        cur.execute("SELECT channel, COUNT(*) FROM sales GROUP BY channel ORDER BY channel")
        channels = {r[0]: int(r[1]) for r in cur.fetchall()}
    return {
        "range": {"from": DATE_FROM.isoformat(), "to": DATE_TO.isoformat()},
        "as_of": last_sale.astimezone(UTC).date().isoformat() if last_sale else None,
        "suppliers": int(n_suppliers),
        "products": int(n_products),
        "sales_rows": int(sales_rows),
        "expense_rows": int(expense_rows),
        "income": float(income),
        "expense": float(expense),
        "net": float(income - expense),
        "channels": channels,
        "critical": critical,
        "near_critical": near,
        "top_profit": top,
        "monthly": monthly,
    }


def run(url: str, reset: bool = True) -> dict[str, Any]:
    """Veriyi üretir, yazar ve özet döner. Aynı tohum -> aynı özet."""
    rng = np.random.default_rng(SEED)
    Faker.seed(SEED)
    fake = Faker("tr_TR")

    suppliers = _gen_suppliers(fake)
    products = _gen_products(rng)
    sales = _gen_sales(rng, products)
    leader_fix = _ensure_profit_leader(rng, sales, products)
    _set_stock(rng, products)
    expenses = _gen_expenses(rng, fake, products, suppliers)

    t0 = time.perf_counter()
    try:
        with psycopg.connect(url) as conn:
            _write(conn, reset, suppliers, products, sales, expenses)
            conn.commit()
            summary = _summary(conn)
    except psycopg.errors.UndefinedTable as e:
        raise SystemExit(
            f"Tablo yok ({e.diag.message_primary}). Önce şemayı uygula: "
            'psql "$DATABASE_URL" -f docs/schema.sql'
        ) from e
    summary["leader_fix_rows"] = leader_fix
    summary["seconds"] = round(time.perf_counter() - t0, 2)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="OtoHesap sentetik veri (seed=42)")
    parser.add_argument("--reset", action="store_true", help="tabloları boşaltıp yeniden doldur")
    parser.add_argument("--url", help="postgresql://... (yoksa DATABASE_URL / .env)")
    args = parser.parse_args(argv)
    summary = run(resolve_url(args.url), reset=args.reset)
    json.dump(summary, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
