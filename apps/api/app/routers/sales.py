"""Satış CRUD — AGENTS.md §6. Satış eklemek stoğu düşürür, silmek iade eder. Sahibi: Murat."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Product, Sale
from ..schemas.core import SaleCreate, SaleListOut, SaleOut, SaleUpdate

router = APIRouter(prefix="/api", tags=["sales"])

DbDep = Annotated[Session, Depends(get_db)]

SALE_NOT_FOUND = "Satış bulunamadı"
PRODUCT_NOT_FOUND = "Ürün bulunamadı"


def as_utc(dt: datetime | None) -> datetime:
    """Boşsa şimdi; saat dilimi yoksa UTC varsayılır."""
    if dt is None:
        return datetime.now(UTC)
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


def _to_out(sale: Sale, product_name: str) -> SaleOut:
    return SaleOut(
        id=sale.id,
        sold_at=sale.sold_at,
        product_id=sale.product_id,
        product_name=product_name,
        qty=sale.qty,
        unit_price=float(sale.unit_price),
        total=float(sale.total),
        channel=sale.channel,
    )


def _get_sale(db: Session, sale_id: int) -> Sale:
    sale = db.get(Sale, sale_id)
    if sale is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=SALE_NOT_FOUND)
    return sale


def _lock_product(db: Session, product_id: int) -> Product:
    """Ürün satırını kilitler (stok güncellemesi yarışmasın)."""
    product = db.get(Product, product_id, with_for_update=True)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=PRODUCT_NOT_FOUND)
    return product


def _move_stock(product: Product, qty: int) -> None:
    """qty > 0: stoktan düşer (yetersizse 400); qty < 0: iade eder."""
    if qty > 0 and product.stock_qty < qty:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail=f"Stok yetersiz: {product.stock_qty} adet var"
        )
    product.stock_qty -= qty


@router.get("/sales", response_model=SaleListOut)
def list_sales(
    db: DbDep,
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    q: Annotated[str | None, Query()] = None,
) -> SaleListOut:
    base = select(Sale, Product.name).join(Product, Sale.product_id == Product.id)
    if q and q.strip():
        base = base.where(Product.name.ilike(f"%{q.strip()}%"))
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = db.execute(
        base.order_by(Sale.sold_at.desc(), Sale.id.desc()).limit(limit).offset(offset)
    ).all()
    return SaleListOut(items=[_to_out(sale, name) for sale, name in rows], total=int(total))


@router.post("/sales", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
def create_sale(body: SaleCreate, db: DbDep) -> SaleOut:
    product = _lock_product(db, body.product_id)
    _move_stock(product, body.qty)
    unit_price = body.unit_price if body.unit_price is not None else product.sale_price
    sale = Sale(
        sold_at=as_utc(body.sold_at),
        product_id=product.id,
        qty=body.qty,
        unit_price=unit_price,
        total=unit_price * body.qty,
        channel=body.channel,
    )
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return _to_out(sale, product.name)


@router.put("/sales/{sale_id}", response_model=SaleOut)
def update_sale(sale_id: int, body: SaleUpdate, db: DbDep) -> SaleOut:
    sale = _get_sale(db, sale_id)
    data = body.model_dump(exclude_unset=True)
    new_product_id = data.get("product_id") or sale.product_id
    new_qty = data.get("qty") or sale.qty

    old_product = _lock_product(db, sale.product_id)
    if new_product_id != sale.product_id:
        product = _lock_product(db, new_product_id)
        _move_stock(product, new_qty)  # önce yeni ürün (yetersizse hiçbir şey değişmez)
        old_product.stock_qty += sale.qty
        default_price = product.sale_price
    else:
        product = old_product
        _move_stock(product, new_qty - sale.qty)  # yalnız fark
        default_price = sale.unit_price

    if data.get("unit_price") is not None:
        unit_price = data["unit_price"]
    elif "unit_price" in data:  # açıkça null: ürünün fiyatı
        unit_price = product.sale_price
    else:
        unit_price = default_price

    sale.product_id = product.id
    sale.qty = new_qty
    sale.unit_price = unit_price
    sale.total = unit_price * new_qty
    if data.get("sold_at") is not None:
        sale.sold_at = as_utc(data["sold_at"])
    if data.get("channel") is not None:
        sale.channel = data["channel"]
    db.commit()
    db.refresh(sale)
    return _to_out(sale, product.name)


@router.delete("/sales/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(sale_id: int, db: DbDep) -> Response:
    sale = _get_sale(db, sale_id)
    product = _lock_product(db, sale.product_id)
    product.stock_qty += sale.qty  # iade
    db.delete(sale)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
