import enum

from sqlalchemy import Boolean, DateTime, Enum, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class DiscountTypeEnum(str, enum.Enum):
    PERCENT = "percent"
    FLAT = "flat"


class Promotion(Base, TimestampMixin):
    __tablename__ = "promotions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    discount_type: Mapped[DiscountTypeEnum] = mapped_column(Enum(DiscountTypeEnum), nullable=False)
    discount_value: Mapped[float] = mapped_column(Float, nullable=False)
    minimum_purchase: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    maximum_discount: Mapped[float] = mapped_column(Float, nullable=True)
    start_date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    expiry_date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    usage_limit: Mapped[int] = mapped_column(Integer, nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
