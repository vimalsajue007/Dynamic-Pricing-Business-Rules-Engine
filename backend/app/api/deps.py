from typing import Optional

from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AppException, PermissionDeniedException
from app.core.security import decode_token
from app.models.user import RoleEnum, User

# auto_error=False lets us raise our own AppException (consistent JSON error
# shape) instead of FastAPI's default 403 "Not authenticated" response.
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise AppException("Not authenticated", status.HTTP_401_UNAUTHORIZED)

    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise AppException("Invalid or expired token", status.HTTP_401_UNAUTHORIZED)

    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user:
        raise AppException("User not found", status.HTTP_401_UNAUTHORIZED)
    if not user.is_active:
        raise AppException("Account is deactivated", status.HTTP_403_FORBIDDEN)
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != RoleEnum.ADMIN:
        raise PermissionDeniedException("Administrator privileges required")
    return current_user