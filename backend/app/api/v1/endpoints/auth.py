from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import AppException, ConflictException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import RoleEnum, User
from app.schemas.auth import RefreshRequest, TokenResponse, UserLogin, UserOut, UserRegister
from app.schemas.common import APIResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=APIResponse[UserOut], status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise ConflictException("A user with this email already exists")

    is_first_user = db.query(User).count() == 0
    user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=RoleEnum.ADMIN if is_first_user else RoleEnum.USER,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return APIResponse(message="Registration successful", data=UserOut.model_validate(user))


@router.post("/login", response_model=APIResponse[TokenResponse])
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise AppException("Incorrect email or password", status.HTTP_401_UNAUTHORIZED)
    if not user.is_active:
        raise AppException("Account is deactivated", status.HTTP_403_FORBIDDEN)

    tokens = TokenResponse(
        access_token=create_access_token(user.email, user.role.value),
        refresh_token=create_refresh_token(user.email, user.role.value),
    )
    return APIResponse(message="Login successful", data=tokens)


@router.post("/refresh", response_model=APIResponse[TokenResponse])
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    decoded = decode_token(payload.refresh_token)
    if not decoded or decoded.get("type") != "refresh":
        raise AppException("Invalid or expired refresh token", status.HTTP_401_UNAUTHORIZED)

    user = db.query(User).filter(User.email == decoded.get("sub")).first()
    if not user or not user.is_active:
        raise AppException("User not found or inactive", status.HTTP_401_UNAUTHORIZED)

    tokens = TokenResponse(
        access_token=create_access_token(user.email, user.role.value),
        refresh_token=create_refresh_token(user.email, user.role.value),
    )
    return APIResponse(message="Token refreshed", data=tokens)


@router.get("/me", response_model=APIResponse[UserOut])
def get_me(current_user: User = Depends(get_current_user)):
    return APIResponse(data=UserOut.model_validate(current_user))
