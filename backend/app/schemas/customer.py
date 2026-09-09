from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.customer import CustomerTypeEnum


class CustomerBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    customer_type: CustomerTypeEnum = CustomerTypeEnum.REGULAR
    location: Optional[str] = None
    category: Optional[str] = None
    is_active: bool = True


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    customer_type: Optional[CustomerTypeEnum] = None
    location: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerOut(CustomerBase):
    id: int

    class Config:
        from_attributes = True
