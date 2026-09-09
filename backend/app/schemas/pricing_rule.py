from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.pricing_rule import (
    ActionTypeEnum,
    ConditionFieldEnum,
    OperatorEnum,
    RuleLogicEnum,
)


class RuleConditionBase(BaseModel):
    field: ConditionFieldEnum
    operator: OperatorEnum
    value: str


class RuleActionBase(BaseModel):
    action_type: ActionTypeEnum
    value: float
    max_amount: Optional[float] = None


class PricingRuleBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: Optional[str] = None
    priority: int = Field(default=100, ge=1, le=10000)
    condition_logic: RuleLogicEnum = RuleLogicEnum.AND
    is_exclusive: bool = False
    is_stackable: bool = True
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = True


class PricingRuleCreate(PricingRuleBase):
    conditions: List[RuleConditionBase] = Field(default_factory=list)
    actions: List[RuleActionBase] = Field(min_length=1)


class PricingRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    condition_logic: Optional[RuleLogicEnum] = None
    is_exclusive: Optional[bool] = None
    is_stackable: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    conditions: Optional[List[RuleConditionBase]] = None
    actions: Optional[List[RuleActionBase]] = None


class RuleConditionOut(RuleConditionBase):
    id: int

    class Config:
        from_attributes = True


class RuleActionOut(RuleActionBase):
    id: int

    class Config:
        from_attributes = True


class PricingRuleOut(PricingRuleBase):
    id: int
    conditions: List[RuleConditionOut] = []
    actions: List[RuleActionOut] = []

    class Config:
        from_attributes = True
