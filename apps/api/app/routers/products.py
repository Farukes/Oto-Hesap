"""Ürünler: GET /api/products (is_critical, open_order_id), PATCH /api/products/{id}. Murat."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Product, PurchaseOrder, Supplier
from ..schemas.core import ProductOut, ProductPatch
from ..services.agent import OPEN_STATUSES

router = APIRouter(prefix="/api", tags=["products"])

DbDep = Annotated[Session, Depends(get_db)]

PRODUCT_NOT_FOUND = "Ürün bulunamadı"

# Ürün için açık (taslak/onaylı/gönderildi) en yeni sipariş; yoksa NULL.
_open_order_id = (
    select(PurchaseOrder.id)
    .where(
        PurchaseOrder.product_id == Product.id,
        PurchaseOrder.status.in_(OPEN_STATUSES),  # draft/approved/sent — ajanla birebir
    )
    .order_by(PurchaseOrder.created_at.desc(), PurchaseOrder.id.desc())
    .limit(1)
    .correlate(Product)
    .scalar_subquery()
)

_products_stmt = (
    select(Product, Supplier.name, _open_order_id)
    .outerjoin(Supplier, Product.supplier_id == Supplier.id)
    .order_by(Product.id)
)


def _to_out(product: Product, supplier_name: str | None, open_order_id: int | None) -> ProductOut:
    return ProductOut(
        id=product.id,
        name=product.name,
        category=product.category,
        unit_cost=float(product.unit_cost),
        sale_price=float(product.sale_price),
        stock_qty=product.stock_qty,
        reorder_point=product.reorder_point,
        target_stock=product.target_stock,
        supplier_id=product.supplier_id,
        supplier_name=supplier_name,
        is_critical=product.is_critical,
        open_order_id=open_order_id,
    )


@router.get("/products", response_model=list[ProductOut])
def list_products(db: DbDep) -> list[ProductOut]:
    rows = db.execute(_products_stmt).all()
    return [_to_out(p, s, o) for p, s, o in rows]


@router.patch("/products/{product_id}", response_model=ProductOut)
def patch_product(product_id: int, body: ProductPatch, db: DbDep) -> ProductOut:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=PRODUCT_NOT_FOUND)
    for key, value in body.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(product, key, value)
    db.commit()
    row = db.execute(_products_stmt.where(Product.id == product_id)).one()
    return _to_out(*row)
