from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PricingRequest(BaseModel):
    product_id: int
    customer_id: Optional[int] = None
    quantity: int = Field(default=1, ge=1)
    location: Optional[str] = None
    calculation_date: Optional[date] = None
    promo_code: Optional[str] = None


class AppliedRuleDetail(BaseModel):
    rule_id: Optional[int] = None
    rule_name: str
    action_type: str
    discount_amount: float = 0
    surcharge_amount: float = 0
    stacked: bool = True


class NonMatchedRuleDetail(BaseModel):
    rule_id: int
    rule_name: str
    reason: str


class PromotionDetail(BaseModel):
    code: str
    discount_amount: float
    valid: bool
    message: Optional[str] = None


class PricingResult(BaseModel):
    product_id: int
    product_name: str
    base_price: float
    quantity: int
    subtotal: float
    applied_rules: List[AppliedRuleDetail] = []
    rule_discount_total: float = 0
    promotion: Optional[PromotionDetail] = None
    promotion_discount: float = 0
    surcharge_total: float = 0
    taxable_amount: float = 0
    tax_rate_percent: float
    tax_amount: float
    final_price: float


class RuleTestRequest(PricingRequest):
    pass


class RuleTestResult(BaseModel):
    pricing: PricingResult
    matched_rules: List[AppliedRuleDetail]
    non_matched_rules: List[NonMatchedRuleDetail]


class PricingHistoryOut(BaseModel):
    id: int
    product_id: int
    customer_id: Optional[int]
    input_parameters: dict
    applied_rules: List[dict]   # was: dict
    promo_code: Optional[str]
    original_price: float
    discount_amount: float
    tax_amount: float
    final_price: float
    calculation_time: datetime

    class Config:
        from_attributes = True
