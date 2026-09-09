from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import ConflictException, NotFoundException
from app.models.promotion import Promotion
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.promotion import PromotionCreate, PromotionOut, PromotionUpdate
from app.services.cache_service import invalidate_promotions

router = APIRouter(prefix="/promotions", tags=["Promotions"])


@router.get("", response_model=APIResponse[PaginatedResponse[PromotionOut]])
def list_promotions(
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Promotion)
    if search:
        q = q.filter(Promotion.code.ilike(f"%{search}%"))
    if is_active is not None:
        q = q.filter(Promotion.is_active == is_active)
    total = q.count()
    items = q.order_by(Promotion.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return APIResponse(
        data=PaginatedResponse(
            items=[PromotionOut.model_validate(p) for p in items],
            total=total, page=page, page_size=page_size,
            total_pages=max((total + page_size - 1) // page_size, 1),
        )
    )


@router.post("", response_model=APIResponse[PromotionOut], status_code=201)
def create_promotion(payload: PromotionCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    code = payload.code.upper().strip()
    if db.query(Promotion).filter(Promotion.code == code).first():
        raise ConflictException("A promotion with this code already exists")
    data = payload.model_dump()
    data["code"] = code
    promo = Promotion(**data)
    db.add(promo)
    db.commit()
    db.refresh(promo)
    invalidate_promotions()
    return APIResponse(message="Promotion created", data=PromotionOut.model_validate(promo))


@router.put("/{promo_id}", response_model=APIResponse[PromotionOut])
def update_promotion(promo_id: int, payload: PromotionUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    promo = db.query(Promotion).filter(Promotion.id == promo_id).first()
    if not promo:
        raise NotFoundException("Promotion not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(promo, k, v)
    db.commit()
    db.refresh(promo)
    invalidate_promotions()
    return APIResponse(message="Promotion updated", data=PromotionOut.model_validate(promo))


@router.delete("/{promo_id}", response_model=APIResponse[None])
def delete_promotion(promo_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    promo = db.query(Promotion).filter(Promotion.id == promo_id).first()
    if not promo:
        raise NotFoundException("Promotion not found")
    db.delete(promo)
    db.commit()
    invalidate_promotions()
    return APIResponse(message="Promotion deleted")
