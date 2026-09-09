from typing import List

from pydantic import BaseModel


class MostAppliedRule(BaseModel):
    rule_name: str
    times_applied: int


class TrendPoint(BaseModel):
    date: str
    count: int


class DashboardSummary(BaseModel):
    total_products: int
    active_pricing_rules: int
    active_promotions: int
    total_discounts_given: float
    pricing_calculation_count: int
    most_applied_rules: List[MostAppliedRule]
    pricing_activity_trend: List[TrendPoint]
