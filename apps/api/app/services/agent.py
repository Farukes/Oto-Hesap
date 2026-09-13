"""Otonom tedarik ajanı — kural tabanlı, deterministik, LLM yok. Sahibi: Ömer.

Akış: kritik ürün (`stock_qty <= reorder_point`) → açık sipariş yoksa taslak → insan onayı
(`POST /api/orders/{id}/approve`) → tedarikçiye mesaj (services/notify).

Tekrar koruması DB düzeyindedir: `ux_open_order_per_product` kısmi tekil indeksi ürün başına
yalnız BİR `draft | approved | sent` siparişe izin verir (docs/schema.sql). Her ürünün insert'i bir
savepoint içinde denenir; `IntegrityError` → ürün `acik_siparis_var` ile atlanır, döngü sürer.
`rejected` açık sayılmaz; reddedilen ürün bir sonraki kontrolde yeniden taslağa düşer.
"""

from __future__ import annotations

import logging
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from ..config import settings
from ..models import Product, PurchaseOrder
from ..schemas.orders import OrderOut

log = logging.getLogger("otohesap.agent")

# Ürün için "açık sipariş" sayılan durumlar. `products.open_order_id` (Murat) aynı kümeyi
# kullanmalı: `from app.services.agent import OPEN_STATUSES`. DB indeksiyle birebir.
OPEN_STATUSES: tuple[str, ...] = ("draft", "approved", "sent")

# `skipped[].reason` kodları (arayüz rozet/metin eşler)
REASON_OPEN_ORDER = "acik_siparis_var"
REASON_NO_SUPPLIER = "tedarikci_yok"

MESSAGE_TEMPLATE = (
    "DEMO · sentetik sipariş #{order_id} — "
    "Merhaba {supplier_name}, {business_name} için sipariş talebi: {product_name} × {qty} adet. "
    "Tahmini tutar {amount} ₺. Teslim süresi {lead_time_days} gün. "
    "Onay için bu mesajı yanıtlayabilirsiniz. — OtoHesap"
)

_TWO_PLACES = Decimal("0.01")


def format_try(value: Decimal | int | float) -> str:
    """tr-TR para biçimi: binlik '.', ondalık ',' — 12500 → '12.500,00'. Locale'e bağımlı değil."""
    quantized = Decimal(value).quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)
    en = f"{quantized:,.2f}"  # 12,500.00 (İngilizce ayraçlar)
    return en.replace(",", "_").replace(".", ",").replace("_", ".")


def build_message(order_id: int, product: Product, qty: int, est_amount: Decimal) -> str:
    supplier = product.supplier
    assert supplier is not None  # çağıran kontrol eder
    return MESSAGE_TEMPLATE.format(
        order_id=order_id,
        supplier_name=supplier.name,
        business_name=settings.business_name,
        product_name=product.name,
        qty=qty,
        amount=format_try(est_amount),
        lead_time_days=supplier.lead_time_days,
    )


def _create_draft(db: Session, product: Product) -> PurchaseOrder:
    """Tek ürün için taslak; savepoint içinde flush eder (id gerekir), tekil indeks çakışırsa
    IntegrityError yükselir ve yalnız bu savepoint geri alınır."""
    qty = max(1, product.target_stock - product.stock_qty)
    est_amount = (Decimal(qty) * Decimal(product.unit_cost)).quantize(_TWO_PLACES)
    with db.begin_nested():
        order = PurchaseOrder(
            product_id=product.id,
            supplier_id=product.supplier_id,
            qty=qty,
            est_amount=est_amount,
            status="draft",
        )
        order.product = product
        order.supplier = product.supplier
        db.add(order)
        db.flush()  # id burada oluşur; indeks çakışması da burada patlar
        order.message_text = build_message(order.id, product, qty, est_amount)
        db.flush()
    return order


def run_check(db: Session) -> dict[str, Any]:
    """Kritik stok kontrolü; taslak siparişleri yazar ve özet döner.

    Dönüş: {"created": n, "drafts": [OrderOut dict...], "skipped": [{"product_id", "reason"}]}
    reason ∈ {"acik_siparis_var", "tedarikci_yok"}
    """
    products = (
        db.execute(
            select(Product)
            .options(selectinload(Product.supplier))
            .where(Product.stock_qty <= Product.reorder_point)
            .order_by(Product.id)
        )
        .scalars()
        .all()
    )

    created: list[PurchaseOrder] = []
    skipped: list[dict[str, Any]] = []
    for product in products:
        if product.supplier_id is None or product.supplier is None:
            skipped.append({"product_id": product.id, "reason": REASON_NO_SUPPLIER})
            continue
        try:
            order = _create_draft(db, product)
        except IntegrityError:
            skipped.append({"product_id": product.id, "reason": REASON_OPEN_ORDER})
            continue
        created.append(order)

    db.commit()
    for order in created:
        db.refresh(order)  # created_at sunucu varsayılanı

    drafts = [OrderOut.model_validate(o).model_dump(mode="json") for o in created]
    log.info(
        "ajan: %d kritik ürün, %d taslak, %d atlandı", len(products), len(drafts), len(skipped)
    )
    for s in skipped:
        log.info("ajan atladı: ürün #%s — %s", s["product_id"], s["reason"])
    return {"created": len(drafts), "drafts": drafts, "skipped": skipped}
