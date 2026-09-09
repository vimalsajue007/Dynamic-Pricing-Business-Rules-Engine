from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.redis_client import cache_get, cache_set
from app.models.pricing_calculation import CalculationRule, PricingCalculation
from app.models.pricing_rule import PricingRule
from app.models.product import Product
from app.models.promotion import Promotion
from app.schemas.common import APIResponse
from app.schemas.dashboard import DashboardSummary, MostAppliedRule, TrendPoint
from app.services.cache_service import DASHBOARD_PREFIX

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=APIResponse[DashboardSummary])
def dashboard_summary(db: Session = Depends(get_db), _=Depends(get_current_user)):
    cache_key = f"{DASHBOARD_PREFIX}summary"
    cached = cache_get(cache_key)
    if cached:
        return APIResponse(data=DashboardSummary(**cached))

    total_products = db.query(func.count(Product.id)).scalar() or 0
    active_rules = db.query(func.count(PricingRule.id)).filter(PricingRule.is_active == True).scalar() or 0  # noqa: E712
    active_promotions = (
        db.query(func.count(Promotion.id)).filter(Promotion.is_active == True).scalar() or 0  # noqa: E712
    )
    calc_count = db.query(func.count(PricingCalculation.id)).scalar() or 0
    total_discounts = db.query(func.coalesce(func.sum(PricingCalculation.discount_amount), 0)).scalar() or 0

    most_applied_rows = (
        db.query(CalculationRule.rule_name, func.count(CalculationRule.id).label("cnt"))
        .group_by(CalculationRule.rule_name)
        .order_by(func.count(CalculationRule.id).desc())
        .limit(5)
        .all()
    )
    most_applied = [MostAppliedRule(rule_name=row[0], times_applied=row[1]) for row in most_applied_rows]

    since = date.today() - timedelta(days=13)
    trend_rows = (
        db.query(func.date(PricingCalculation.calculation_time).label("d"), func.count(PricingCalculation.id))
        .filter(func.date(PricingCalculation.calculation_time) >= since)
        .group_by("d")
        .order_by("d")
        .all()
    )
    trend_map = {str(row[0]): row[1] for row in trend_rows}
    trend = []
    for i in range(14):
        d = since + timedelta(days=i)
        trend.append(TrendPoint(date=str(d), count=trend_map.get(str(d), 0)))

    summary = DashboardSummary(
        total_products=total_products,
        active_pricing_rules=active_rules,
        active_promotions=active_promotions,
        total_discounts_given=float(total_discounts),
        pricing_calculation_count=calc_count,
        most_applied_rules=most_applied,
        pricing_activity_trend=trend,
    )
    cache_set(cache_key, summary.model_dump(), ttl=60)
    return APIResponse(data=summary)
