"""Sipariş (purchase_orders) yanıt şemaları — AGENTS.md §6. Sahibi: Ömer.

`OrderOut` ORM nesnesinden doğrudan üretilir (`from_attributes=True`); ürün ve tedarikçi adları
ilişkiler üzerinden `AliasPath` ile okunur. Para alanları JSON'da number (float) döner.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import AliasPath, BaseModel, ConfigDict, Field

OrderStatus = Literal["draft", "approved", "sent", "rejected"]


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    created_at: datetime
    product_id: int
    product_name: str = Field(validation_alias=AliasPath("product", "name"))
    supplier_id: int
    supplier_name: str = Field(validation_alias=AliasPath("supplier", "name"))
    supplier_channel: str = Field(validation_alias=AliasPath("supplier", "contact_channel"))
    qty: int
    est_amount: float | None
    status: OrderStatus
    message_text: str | None
    sent_at: datetime | None
    notify_ref: str | None  # Telegram message_id (str) ya da 'dry-run'; gönderim izi


class NotifyResult(BaseModel):
    """`services/notify.send_message` dönüşü (fazla anahtarlar yok sayılır)."""

    ok: bool
    dry_run: bool
    channel: str
    message_id: int | None = None


class OrderApproveOut(OrderOut):
    notify: NotifyResult
