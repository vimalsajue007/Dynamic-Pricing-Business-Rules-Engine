from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.models.customer import Customer
from app.models.pricing_calculation import CalculationRule, PricingCalculation
from app.models.pricing_rule import PricingRule
from app.models.product import Product
from app.models.promotion import Promotion
from app.models.user import User
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.pricing import (
    PricingHistoryOut,
    PricingRequest,
    PricingResult,
    RuleTestRequest,
    RuleTestResult,
)
from app.services.cache_service import invalidate_dashboard
from app.services.pricing_engine import calculate_price

router = APIRouter(prefix="/pricing", tags=["Pricing Engine"])


def _resolve_inputs(db: Session, payload: PricingRequest):
    product = db.query(Product).filter(Product.id == payload.product_id, Product.is_active == True).first()  # noqa: E712
    if not product:
        raise NotFoundException("Active product not found")

    customer: Optional[Customer] = None
    if payload.customer_id:
        customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
        if not customer:
            raise NotFoundException("Customer not found")

    promotion: Optional[Promotion] = None
    if payload.promo_code:
        promotion = db.query(Promotion).filter(Promotion.code == payload.promo_code.upper().strip()).first()

    rules = db.query(PricingRule).filter(PricingRule.is_active == True).all()  # noqa: E712
    calc_date = payload.calculation_date or date.today()
    return product, customer, promotion, rules, calc_date


@router.post("/preview", response_model=APIResponse[PricingResult])
def pricing_preview(
    payload: PricingRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Compute and persist a pricing calculation (used by the customer-facing preview screen)."""
    product, customer, promotion, rules, calc_date = _resolve_inputs(db, payload)

    result, _outcome = calculate_price(
        product=product,
        customer=customer,
        quantity=payload.quantity,
        location=payload.location,
        calculation_date=calc_date,
        rules=rules,
        promotion=promotion,
    )

    record = PricingCalculation(
        product_id=product.id,
        customer_id=customer.id if customer else None,
        input_parameters=payload.model_dump(mode="json"),
        applied_rules=[r.model_dump() for r in result.applied_rules],
        promo_code=payload.promo_code.upper() if payload.promo_code else None,
        original_price=result.subtotal,
        discount_amount=result.rule_discount_total + result.promotion_discount,
        tax_amount=result.tax_amount,
        final_price=result.final_price,
    )
    db.add(record)
    db.flush()
    for r in result.applied_rules:
        db.add(
            CalculationRule(
                calculation_id=record.id,
                rule_id=r.rule_id,
                rule_name=r.rule_name,
                discount_applied=r.discount_amount,
            )
        )
    db.commit()
    invalidate_dashboard()

    return APIResponse(message="Pricing calculated", data=result)


@router.post("/test", response_model=APIResponse[RuleTestResult])
def test_rules(
    payload: RuleTestRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Dry-run a pricing calculation without persisting history — for testing rules before activation."""
    product, customer, promotion, rules, calc_date = _resolve_inputs(db, payload)

    result, outcome = calculate_price(
        product=product,
        customer=customer,
        quantity=payload.quantity,
        location=payload.location,
        calculation_date=calc_date,
        rules=rules,
        promotion=promotion,
    )

    return APIResponse(
        data=RuleTestResult(
            pricing=result,
            matched_rules=outcome.matched,
            non_matched_rules=outcome.non_matched,
        )
    )


@router.get("/history", response_model=APIResponse[PaginatedResponse[PricingHistoryOut]])
def pricing_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    product_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(PricingCalculation)
    if product_id:
        q = q.filter(PricingCalculation.product_id == product_id)
    if customer_id:
        q = q.filter(PricingCalculation.customer_id == customer_id)
    total = q.count()
    items = (
        q.order_by(PricingCalculation.calculation_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return APIResponse(
        data=PaginatedResponse(
            items=[PricingHistoryOut.model_validate(i) for i in items],
            total=total, page=page, page_size=page_size,
            total_pages=max((total + page_size - 1) // page_size, 1),
        )
    )
