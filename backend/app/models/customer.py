import enum

from sqlalchemy import Boolean, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class CustomerTypeEnum(str, enum.Enum):
    REGULAR = "Regular"
    PREMIUM = "Premium"
    BUSINESS = "Business"
    WHOLESALE = "Wholesale"


class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    customer_type: Mapped[CustomerTypeEnum] = mapped_column(
        Enum(CustomerTypeEnum), default=CustomerTypeEnum.REGULAR, nullable=False, index=True
    )
    location: Mapped[str] = mapped_column(String(120), nullable=True, index=True)
    category: Mapped[str] = mapped_column(String(120), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
