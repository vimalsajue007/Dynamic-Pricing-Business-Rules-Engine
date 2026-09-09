from pydantic import BaseModel, EmailStr, Field

from app.models.user import RoleEnum


class UserRegister(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: RoleEnum
    is_active: bool

    class Config:
        from_attributes = True


class UserUpdateStatus(BaseModel):
    is_active: bool

class UserUpdateRole(BaseModel):
    role: RoleEnum