import enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class ConditionFieldEnum(str, enum.Enum):
    CUSTOMER_TYPE = "customer_type"
    QUANTITY = "quantity"
    LOCATION = "location"
    CATEGORY = "category"
    PRODUCT = "product"
    ORDER_TOTAL = "order_total"
    DATE = "date"


class OperatorEnum(str, enum.Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    GREATER_OR_EQUAL = "greater_or_equal"
    LESS_THAN = "less_than"
    LESS_OR_EQUAL = "less_or_equal"
    IN = "in"


class ActionTypeEnum(str, enum.Enum):
    PERCENT_DISCOUNT = "percent_discount"
    FLAT_DISCOUNT = "flat_discount"
    SURCHARGE_PERCENT = "surcharge_percent"
    SURCHARGE_FLAT = "surcharge_flat"
    FIXED_PRICE = "fixed_price"


class RuleLogicEnum(str, enum.Enum):
    AND = "AND"
    OR = "OR"


class PricingRule(Base, TimestampMixin):
    __tablename__ = "pricing_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False, index=True)
    condition_logic: Mapped[RuleLogicEnum] = mapped_column(
        Enum(RuleLogicEnum), default=RuleLogicEnum.AND, nullable=False
    )
    # if True, no lower-priority (higher number) rule is evaluated after this one matches
    is_exclusive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # whether this rule's discount can be combined (stacked) with other matched rules
    is_stackable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    start_date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    conditions: Mapped[list["RuleCondition"]] = relationship(
        back_populates="rule", cascade="all, delete-orphan"
    )
    actions: Mapped[list["RuleAction"]] = relationship(
        back_populates="rule", cascade="all, delete-orphan"
    )


class RuleCondition(Base, TimestampMixin):
    __tablename__ = "rule_conditions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("pricing_rules.id"), nullable=False, index=True)
    field: Mapped[ConditionFieldEnum] = mapped_column(Enum(ConditionFieldEnum), nullable=False)
    operator: Mapped[OperatorEnum] = mapped_column(Enum(OperatorEnum), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)

    rule: Mapped["PricingRule"] = relationship(back_populates="conditions")


class RuleAction(Base, TimestampMixin):
    __tablename__ = "rule_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("pricing_rules.id"), nullable=False, index=True)
    action_type: Mapped[ActionTypeEnum] = mapped_column(Enum(ActionTypeEnum), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    max_amount: Mapped[float] = mapped_column(Float, nullable=True)

    rule: Mapped["PricingRule"] = relationship(back_populates="actions")
