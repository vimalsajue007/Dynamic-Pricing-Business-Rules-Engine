from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import ConflictException, NotFoundException
from app.models.product import Category
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.product import CategoryCreate, CategoryOut, CategoryUpdate
from app.services.cache_service import invalidate_products

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=APIResponse[PaginatedResponse[CategoryOut]])
def list_categories(
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Category)
    if search:
        q = q.filter(Category.name.ilike(f"%{search}%"))
    if is_active is not None:
        q = q.filter(Category.is_active == is_active)
    total = q.count()
    items = q.order_by(Category.name).offset((page - 1) * page_size).limit(page_size).all()
    return APIResponse(
        data=PaginatedResponse(
            items=[CategoryOut.model_validate(c) for c in items],
            total=total, page=page, page_size=page_size,
            total_pages=max((total + page_size - 1) // page_size, 1),
        )
    )


@router.post("", response_model=APIResponse[CategoryOut], status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(Category).filter(Category.name == payload.name).first():
        raise ConflictException("Category already exists")
    category = Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    invalidate_products()
    return APIResponse(message="Category created", data=CategoryOut.model_validate(category))


@router.put("/{category_id}", response_model=APIResponse[CategoryOut])
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise NotFoundException("Category not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(category, k, v)
    db.commit()
    db.refresh(category)
    invalidate_products()
    return APIResponse(message="Category updated", data=CategoryOut.model_validate(category))


@router.delete("/{category_id}", response_model=APIResponse[None])
def delete_category(category_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise NotFoundException("Category not found")
    db.delete(category)
    db.commit()
    invalidate_products()
    return APIResponse(message="Category deleted")
