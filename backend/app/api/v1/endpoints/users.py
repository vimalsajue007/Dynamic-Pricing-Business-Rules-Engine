from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import AppException, NotFoundException
from app.models.user import User
from app.schemas.auth import UserOut, UserUpdateRole, UserUpdateStatus
from app.schemas.common import APIResponse, PaginatedResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=APIResponse[PaginatedResponse[UserOut]])
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    q = db.query(User)
    if search:
        q = q.filter(User.full_name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%"))
    total = q.count()
    items = q.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return APIResponse(
        data=PaginatedResponse(
            items=[UserOut.model_validate(u) for u in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=max((total + page_size - 1) // page_size, 1),
        )
    )


@router.patch("/{user_id}/status", response_model=APIResponse[UserOut])
def update_user_status(
    user_id: int, payload: UserUpdateStatus, db: Session = Depends(get_db), _=Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("User not found")
    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return APIResponse(message="User status updated", data=UserOut.model_validate(user))


@router.patch("/{user_id}/role", response_model=APIResponse[UserOut])
def update_user_role(
    user_id: int,
    payload: UserUpdateRole,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    if user_id == current_admin.id:
        raise AppException("You cannot change your own role", 400)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("User not found")
    user.role = payload.role
    db.commit()
    db.refresh(user)
    return APIResponse(message="User role updated", data=UserOut.model_validate(user))