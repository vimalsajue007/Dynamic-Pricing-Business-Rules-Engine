from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, require_admin
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import ConflictException, NotFoundException
from app.models.product import Product
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.services.cache_service import invalidate_products

router = APIRouter(prefix="/products", tags=["Products"])

SORTABLE_FIELDS = {"name": Product.name, "base_price": Product.base_price, "created_at": Product.created_at}


@router.get("", response_model=APIResponse[PaginatedResponse[ProductOut]])
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    sort_by: str = Query("created_at"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Product).options(joinedload(Product.category))
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%"))
    if category_id is not None:
        q = q.filter(Product.category_id == category_id)
    if is_active is not None:
        q = q.filter(Product.is_active == is_active)

    sort_col = SORTABLE_FIELDS.get(sort_by, Product.created_at)
    q = q.order_by(asc(sort_col) if sort_dir == "asc" else desc(sort_col))

    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return APIResponse(
        data=PaginatedResponse(
            items=[ProductOut.model_validate(p) for p in items],
            total=total, page=page, page_size=page_size,
            total_pages=max((total + page_size - 1) // page_size, 1),
        )
    )


@router.get("/{product_id}", response_model=APIResponse[ProductOut])
def get_product(product_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    product = db.query(Product).options(joinedload(Product.category)).filter(Product.id == product_id).first()
    if not product:
        raise NotFoundException("Product not found")
    return APIResponse(data=ProductOut.model_validate(product))


@router.post("", response_model=APIResponse[ProductOut], status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(Product).filter(Product.sku == payload.sku).first():
        raise ConflictException("A product with this SKU already exists")
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    invalidate_products()
    return APIResponse(message="Product created", data=ProductOut.model_validate(product))


@router.put("/{product_id}", response_model=APIResponse[ProductOut])
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise NotFoundException("Product not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(product, k, v)
    db.commit()
    db.refresh(product)
    invalidate_products()
    return APIResponse(message="Product updated", data=ProductOut.model_validate(product))


@router.delete("/{product_id}", response_model=APIResponse[None])
def delete_product(product_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise NotFoundException("Product not found")
    db.delete(product)
    db.commit()
    invalidate_products()
    return APIResponse(message="Product deleted")
