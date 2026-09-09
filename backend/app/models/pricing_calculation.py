from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PricingCalculation(Base):
    __tablename__ = "pricing_calculations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=True, index=True)
    input_parameters: Mapped[dict] = mapped_column(JSON, nullable=False)
    applied_rules: Mapped[dict] = mapped_column(JSON, nullable=False)
    promo_code: Mapped[str] = mapped_column(String(50), nullable=True)
    original_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    discount_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    final_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    calculation_time: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), index=True)

    calculation_rules: Mapped[list["CalculationRule"]] = relationship(
        back_populates="calculation", cascade="all, delete-orphan"
    )


class CalculationRule(Base):
    """Join table recording exactly which rules fired for a given calculation."""

    __tablename__ = "calculation_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    calculation_id: Mapped[int] = mapped_column(
        ForeignKey("pricing_calculations.id"), nullable=False, index=True
    )
    rule_id: Mapped[int] = mapped_column(ForeignKey("pricing_rules.id"), nullable=True, index=True)
    rule_name: Mapped[str] = mapped_column(String(150), nullable=False)
    discount_applied: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    calculation: Mapped["PricingCalculation"] = relationship(back_populates="calculation_rules")
