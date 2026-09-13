"""orders uçları — AGENTS.md §6 sözleşmesi. Sahibi: Ömer.

Durum makinesi: draft → approved → sent | rejected
- approve: draft → approved → (mesaj) → sent. Mesaj başarısızsa `approved` kalır, 502.
  approved'a tekrar approve = yeniden gönderme denemesi. sent/rejected'a approve = 409.
- reject: draft | approved → rejected; aksi 409.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..db import get_db
from ..models import PurchaseOrder
from ..schemas.orders import NotifyResult, OrderApproveOut, OrderOut, OrderStatus
from ..services import notify

log = logging.getLogger("otohesap.orders")

router = APIRouter(prefix="/api", tags=["orders"])
DbDep = Annotated[Session, Depends(get_db)]

NOT_FOUND = "Sipariş bulunamadı"
SEND_FAILED = "Mesaj gönderilemedi; sipariş onaylı bekliyor, tekrar deneyin."


def _base_query():
    return select(PurchaseOrder).options(
        joinedload(PurchaseOrder.product), joinedload(PurchaseOrder.supplier)
    )


def _get_or_404(db: Session, order_id: int) -> PurchaseOrder:
    order = db.execute(_base_query().where(PurchaseOrder.id == order_id)).scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail=NOT_FOUND)
    return order


def _already(order: PurchaseOrder) -> HTTPException:
    return HTTPException(status_code=409, detail=f"Sipariş zaten {order.status} durumunda.")


def _notify_ref(result: dict) -> str:
    """Gönderim izi: dry-run'da 'dry-run', gerçek gönderimde Telegram message_id (string)."""
    if result.get("dry_run"):
        return "dry-run"
    message_id = result.get("message_id")
    return str(message_id) if message_id is not None else "sent"


@router.get("/orders", response_model=list[OrderOut])
def list_orders(
    db: DbDep,
    status: Annotated[OrderStatus | None, Query()] = None,
) -> list[PurchaseOrder]:
    stmt = _base_query().order_by(PurchaseOrder.created_at.desc(), PurchaseOrder.id.desc())
    if status is not None:
        stmt = stmt.where(PurchaseOrder.status == status)
    return list(db.execute(stmt).scalars().all())


@router.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: DbDep) -> PurchaseOrder:
    return _get_or_404(db, order_id)


@router.post("/orders/{order_id}/approve", response_model=OrderApproveOut)
def approve_order(order_id: int, db: DbDep) -> OrderApproveOut:
    order = _get_or_404(db, order_id)
    if order.status not in ("draft", "approved"):
        raise _already(order)

    if order.status == "draft":
        order.status = "approved"
        db.commit()  # gönderim çökse bile "onaylandı" kalıcı olsun
        log.info("sipariş #%s onaylandı (ürün #%s)", order.id, order.product_id)

    try:
        result = notify.send_message(order.supplier, order.message_text or "")
    except notify.NotifyError as e:
        log.warning("sipariş #%s gönderilemedi, approved bekliyor: %s", order.id, e)
        raise HTTPException(status_code=502, detail=SEND_FAILED) from e

    order.status = "sent"
    order.sent_at = datetime.now(UTC)
    order.notify_ref = _notify_ref(result)
    db.commit()
    log.info(
        "sipariş #%s gönderildi: kanal=%s dry_run=%s",
        order.id,
        result["channel"],
        result["dry_run"],
    )
    base = OrderOut.model_validate(order)
    return OrderApproveOut(**base.model_dump(), notify=NotifyResult(**result))


@router.post("/orders/{order_id}/reject", response_model=OrderOut)
def reject_order(order_id: int, db: DbDep) -> PurchaseOrder:
    order = _get_or_404(db, order_id)
    if order.status not in ("draft", "approved"):
        raise _already(order)
    order.status = "rejected"
    db.commit()
    log.info("sipariş #%s reddedildi (ürün #%s)", order.id, order.product_id)
    return order
