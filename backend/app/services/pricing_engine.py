"""
Reusable Pricing & Business Rules Engine.

This module is completely independent of FastAPI routes and the HTTP layer.
It receives plain Python inputs (already-loaded ORM objects / primitives)
and returns a structured PricingResult. Routes only orchestrate: fetch data,
call the engine, persist history.

Evaluation flow:
    Base Price -> Applicable Rules -> Discounts -> Additional Charges -> Tax -> Final Price

Rule resolution semantics:
    - Rules are evaluated in ascending `priority` order (lower number = higher priority).
    - A rule "matches" when all (AND) or any (OR) of its conditions are satisfied,
      according to its `condition_logic`.
    - Every matched rule's actions are collected. By default matched rules are
      "stackable" (combined). A rule flagged `is_stackable=False` is applied only
      if no other (already-applied) rule has been applied yet for this calculation;
      i.e. it is exclusive of stacking with anything else.
    - A rule flagged `is_exclusive=True` short-circuits evaluation: once it matches,
      no further (lower-priority) rules are evaluated at all.
    - The combined discount is capped by `settings.MAX_TOTAL_DISCOUNT_PERCENT` of
      the subtotal, guaranteeing predictable, non-negative final prices.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional

from app.core.config import settings
from app.models.customer import Customer
from app.models.pricing_rule import ActionTypeEnum, OperatorEnum, PricingRule, RuleLogicEnum
from app.models.product import Product
from app.models.promotion import DiscountTypeEnum, Promotion
from app.schemas.pricing import (
    AppliedRuleDetail,
    NonMatchedRuleDetail,
    PricingResult,
    PromotionDetail,
)


@dataclass
class PricingContext:
    product: Product
    customer: Optional[Customer]
    quantity: int
    location: Optional[str]
    calculation_date: date
    order_total: float = 0.0


@dataclass
class RuleEvaluationOutcome:
    matched: List[AppliedRuleDetail] = field(default_factory=list)
    non_matched: List[NonMatchedRuleDetail] = field(default_factory=list)


def _coerce(value: str, sample: object):
    """Coerce a rule-condition string value to the type of the field it is compared to."""
    if isinstance(sample, bool):
        return value.strip().lower() in ("true", "1", "yes")
    if isinstance(sample, (int, float)):
        try:
            return float(value)
        except ValueError:
            return value
    return value


def _field_value(ctx: PricingContext, field_name: str):
    mapping = {
        "customer_type": ctx.customer.customer_type.value if ctx.customer else None,
        "quantity": ctx.quantity,
        "location": (ctx.location or (ctx.customer.location if ctx.customer else None)),
        "category": ctx.product.category.name if ctx.product.category else None,
        "product": ctx.product.name,
        "order_total": ctx.order_total,
        "date": ctx.calculation_date.isoformat(),
    }
    return mapping.get(field_name)


def _evaluate_operator(actual, operator: OperatorEnum, expected_raw: str) -> bool:
    if actual is None:
        return False

    if operator == OperatorEnum.IN:
        options = [v.strip() for v in expected_raw.split(",")]
        return str(actual) in options

    expected = _coerce(expected_raw, actual)

    try:
        if operator == OperatorEnum.EQUALS:
            return str(actual).lower() == str(expected).lower() if isinstance(actual, str) else actual == expected
        if operator == OperatorEnum.NOT_EQUALS:
            return str(actual).lower() != str(expected).lower() if isinstance(actual, str) else actual != expected
        if operator == OperatorEnum.GREATER_THAN:
            return float(actual) > float(expected)
        if operator == OperatorEnum.GREATER_OR_EQUAL:
            return float(actual) >= float(expected)
        if operator == OperatorEnum.LESS_THAN:
            return float(actual) < float(expected)
        if operator == OperatorEnum.LESS_OR_EQUAL:
            return float(actual) <= float(expected)
    except (ValueError, TypeError):
        return False
    return False


def _rule_is_within_date_window(rule: PricingRule, on_date: date) -> bool:
    if rule.start_date and on_date < rule.start_date.date():
        return False
    if rule.end_date and on_date > rule.end_date.date():
        return False
    return True


def _rule_matches(rule: PricingRule, ctx: PricingContext) -> bool:
    if not rule.conditions:
        # A rule with no conditions is treated as a global/default rule that always applies.
        return True

    results = []
    for cond in rule.conditions:
        actual = _field_value(ctx, cond.field.value)
        results.append(_evaluate_operator(actual, cond.operator, cond.value))

    if rule.condition_logic == RuleLogicEnum.OR:
        return any(results)
    return all(results)


def evaluate_rules(
    rules: List[PricingRule], ctx: PricingContext, subtotal: float
) -> RuleEvaluationOutcome:
    """Evaluate rules in priority order and produce matched/non-matched detail lists."""
    outcome = RuleEvaluationOutcome()
    ordered = sorted([r for r in rules if r.is_active], key=lambda r: r.priority)

    any_applied = False
    stop_evaluation = False

    for rule in ordered:
        if stop_evaluation:
            outcome.non_matched.append(
                NonMatchedRuleDetail(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    reason="Skipped: an exclusive higher-priority rule already matched",
                )
            )
            continue

        if not _rule_is_within_date_window(rule, ctx.calculation_date):
            outcome.non_matched.append(
                NonMatchedRuleDetail(
                    rule_id=rule.id, rule_name=rule.name, reason="Outside active date window"
                )
            )
            continue

        if not _rule_matches(rule, ctx):
            outcome.non_matched.append(
                NonMatchedRuleDetail(
                    rule_id=rule.id, rule_name=rule.name, reason="Conditions not satisfied"
                )
            )
            continue

        # Non-stackable rule: only apply if nothing else has applied yet.
        if not rule.is_stackable and any_applied:
            outcome.non_matched.append(
                NonMatchedRuleDetail(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    reason="Non-stackable: another rule already applied",
                )
            )
            continue

        for action in rule.actions:
            discount_amount = 0.0
            surcharge_amount = 0.0

            if action.action_type == ActionTypeEnum.PERCENT_DISCOUNT:
                discount_amount = subtotal * (action.value / 100.0)
            elif action.action_type == ActionTypeEnum.FLAT_DISCOUNT:
                discount_amount = action.value
            elif action.action_type == ActionTypeEnum.FIXED_PRICE:
                discount_amount = max(subtotal - action.value, 0.0)
            elif action.action_type == ActionTypeEnum.SURCHARGE_PERCENT:
                surcharge_amount = subtotal * (action.value / 100.0)
            elif action.action_type == ActionTypeEnum.SURCHARGE_FLAT:
                surcharge_amount = action.value

            if action.max_amount is not None:
                discount_amount = min(discount_amount, action.max_amount)

            outcome.matched.append(
                AppliedRuleDetail(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    action_type=action.action_type.value,
                    discount_amount=round(discount_amount, 2),
                    surcharge_amount=round(surcharge_amount, 2),
                    stacked=rule.is_stackable,
                )
            )

        any_applied = True
        if rule.is_exclusive:
            stop_evaluation = True

    return outcome


def validate_promotion(
    promo: Optional[Promotion], subtotal_after_rule_discount: float, on_date: date
) -> Optional[PromotionDetail]:
    if promo is None:
        return None

    if not promo.is_active:
        return PromotionDetail(code=promo.code, discount_amount=0, valid=False, message="Promotion is inactive")
    if promo.start_date and on_date < promo.start_date.date():
        return PromotionDetail(code=promo.code, discount_amount=0, valid=False, message="Promotion not yet started")
    if promo.expiry_date and on_date > promo.expiry_date.date():
        return PromotionDetail(code=promo.code, discount_amount=0, valid=False, message="Promotion has expired")
    if promo.usage_limit is not None and promo.usage_count >= promo.usage_limit:
        return PromotionDetail(code=promo.code, discount_amount=0, valid=False, message="Usage limit reached")
    if subtotal_after_rule_discount < promo.minimum_purchase:
        return PromotionDetail(
            code=promo.code,
            discount_amount=0,
            valid=False,
            message=f"Minimum purchase of {promo.minimum_purchase} not met",
        )

    if promo.discount_type == DiscountTypeEnum.PERCENT:
        amount = subtotal_after_rule_discount * (promo.discount_value / 100.0)
    else:
        amount = promo.discount_value

    if promo.maximum_discount is not None:
        amount = min(amount, promo.maximum_discount)

    amount = min(amount, subtotal_after_rule_discount)

    return PromotionDetail(code=promo.code, discount_amount=round(amount, 2), valid=True)


def calculate_price(
    product: Product,
    customer: Optional[Customer],
    quantity: int,
    location: Optional[str],
    calculation_date: date,
    rules: List[PricingRule],
    promotion: Optional[Promotion],
    tax_rate_percent: Optional[float] = None,
) -> tuple[PricingResult, RuleEvaluationOutcome]:
    """
    The single reusable entry point for computing a final price.
    Independent from the API route — callable from endpoints, background jobs, or tests.
    """
    tax_rate = tax_rate_percent if tax_rate_percent is not None else settings.DEFAULT_TAX_RATE_PERCENT

    subtotal = float(product.base_price) * quantity

    ctx = PricingContext(
        product=product,
        customer=customer,
        quantity=quantity,
        location=location,
        calculation_date=calculation_date,
        order_total=subtotal,
    )

    outcome = evaluate_rules(rules, ctx, subtotal)

    rule_discount_total = sum(r.discount_amount for r in outcome.matched)
    surcharge_total = sum(r.surcharge_amount for r in outcome.matched)

    # Cap combined rule discount so pricing stays predictable and non-negative.
    max_discount = subtotal * (settings.MAX_TOTAL_DISCOUNT_PERCENT / 100.0)
    if rule_discount_total > max_discount:
        scale = max_discount / rule_discount_total if rule_discount_total else 0
        for r in outcome.matched:
            r.discount_amount = round(r.discount_amount * scale, 2)
        rule_discount_total = round(sum(r.discount_amount for r in outcome.matched), 2)

    after_rules = max(subtotal - rule_discount_total + surcharge_total, 0.0)

    promo_detail = validate_promotion(promotion, after_rules, calculation_date)
    promo_discount = promo_detail.discount_amount if (promo_detail and promo_detail.valid) else 0.0

    taxable_amount = max(after_rules - promo_discount, 0.0)
    tax_amount = round(taxable_amount * (tax_rate / 100.0), 2)
    final_price = round(taxable_amount + tax_amount, 2)

    result = PricingResult(
        product_id=product.id,
        product_name=product.name,
        base_price=float(product.base_price),
        quantity=quantity,
        subtotal=round(subtotal, 2),
        applied_rules=outcome.matched,
        rule_discount_total=round(rule_discount_total, 2),
        promotion=promo_detail,
        promotion_discount=round(promo_discount, 2),
        surcharge_total=round(surcharge_total, 2),
        taxable_amount=round(taxable_amount, 2),
        tax_rate_percent=tax_rate,
        tax_amount=tax_amount,
        final_price=final_price,
    )
    return result, outcome
