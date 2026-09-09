from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.promotion import DiscountTypeEnum


class PromotionBase(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    description: Optional[str] = None
    discount_type: DiscountTypeEnum
    discount_value: float = Field(gt=0)
    minimum_purchase: float = Field(default=0, ge=0)
    maximum_discount: Optional[float] = None
    start_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    usage_limit: Optional[int] = Field(default=None, ge=1)
    is_active: bool = True


class PromotionCreate(PromotionBase):
    pass


class PromotionUpdate(BaseModel):
    description: Optional[str] = None
    discount_type: Optional[DiscountTypeEnum] = None
    discount_value: Optional[float] = None
    minimum_purchase: Optional[float] = None
    maximum_discount: Optional[float] = None
    start_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    usage_limit: Optional[int] = None
    is_active: Optional[bool] = None


class PromotionOut(PromotionBase):
    id: int
    usage_count: int

    class Config:
        from_attributes = True
