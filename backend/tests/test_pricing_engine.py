"""
Unit tests for the reusable pricing engine (app/services/pricing_engine.py).
Run with: pytest -v
These tests build lightweight in-memory stand-ins for ORM objects so they
run without a database connection.
"""
from datetime import date, datetime
from types import SimpleNamespace

import pytest

from app.models.pricing_rule import ActionTypeEnum, ConditionFieldEnum, OperatorEnum, RuleLogicEnum
from app.models.customer import CustomerTypeEnum
from app.models.promotion import DiscountTypeEnum
from app.services.pricing_engine import calculate_price


def make_product(price=100.0, category_name=None):
    category = SimpleNamespace(name=category_name) if category_name else None
    return SimpleNamespace(id=1, name="Widget", base_price=price, category=category)


def make_customer(customer_type=CustomerTypeEnum.REGULAR, location=None):
    return SimpleNamespace(id=1, customer_type=customer_type, location=location)


def make_rule(name, priority=100, conditions=None, actions=None, logic=RuleLogicEnum.AND,
              exclusive=False, stackable=True, active=True, start=None, end=None):
    return SimpleNamespace(
        id=hash(name) % 1000,
        name=name,
        priority=priority,
        condition_logic=logic,
        is_exclusive=exclusive,
        is_stackable=stackable,
        is_active=active,
        start_date=start,
        end_date=end,
        conditions=conditions or [],
        actions=actions or [],
    )


def make_condition(field, operator, value):
    return SimpleNamespace(field=field, operator=operator, value=value)


def make_action(action_type, value, max_amount=None):
    return SimpleNamespace(action_type=action_type, value=value, max_amount=max_amount)


def test_no_rules_applies_only_tax():
    product = make_product(price=100)
    result, outcome = calculate_price(
        product=product, customer=None, quantity=1, location=None,
        calculation_date=date.today(), rules=[], promotion=None, tax_rate_percent=10,
    )
    assert result.subtotal == 100
    assert result.rule_discount_total == 0
    assert result.tax_amount == 10
    assert result.final_price == 110


def test_premium_customer_percent_discount():
    product = make_product(price=100)
    customer = make_customer(customer_type=CustomerTypeEnum.PREMIUM)
    rule = make_rule(
        "Premium 10%",
        conditions=[make_condition(ConditionFieldEnum.CUSTOMER_TYPE, OperatorEnum.EQUALS, "Premium")],
        actions=[make_action(ActionTypeEnum.PERCENT_DISCOUNT, 10)],
    )
    result, outcome = calculate_price(
        product=product, customer=customer, quantity=1, location=None,
        calculation_date=date.today(), rules=[rule], promotion=None, tax_rate_percent=0,
    )
    assert result.rule_discount_total == 10
    assert result.final_price == 90
    assert len(outcome.matched) == 1


def test_quantity_threshold_rule():
    product = make_product(price=50)
    rule = make_rule(
        "Bulk 5%",
        conditions=[make_condition(ConditionFieldEnum.QUANTITY, OperatorEnum.GREATER_OR_EQUAL, "10")],
        actions=[make_action(ActionTypeEnum.PERCENT_DISCOUNT, 5)],
    )
    result, _ = calculate_price(
        product=product, customer=None, quantity=10, location=None,
        calculation_date=date.today(), rules=[rule], promotion=None, tax_rate_percent=0,
    )
    assert result.subtotal == 500
    assert result.rule_discount_total == 25  # 5% of 500


def test_and_logic_requires_all_conditions():
    product = make_product(price=100, category_name="Electronics")
    rule = make_rule(
        "Electronics bulk 8%",
        logic=RuleLogicEnum.AND,
        conditions=[
            make_condition(ConditionFieldEnum.CATEGORY, OperatorEnum.EQUALS, "Electronics"),
            make_condition(ConditionFieldEnum.QUANTITY, OperatorEnum.GREATER_OR_EQUAL, "5"),
        ],
        actions=[make_action(ActionTypeEnum.PERCENT_DISCOUNT, 8)],
    )
    # quantity too low -> should NOT match
    result, outcome = calculate_price(
        product=product, customer=None, quantity=2, location=None,
        calculation_date=date.today(), rules=[rule], promotion=None, tax_rate_percent=0,
    )
    assert result.rule_discount_total == 0
    assert len(outcome.non_matched) == 1


def test_stacking_multiple_rules():
    product = make_product(price=200)
    customer = make_customer(customer_type=CustomerTypeEnum.PREMIUM)
    rule1 = make_rule(
        "Premium 10%", priority=10,
        conditions=[make_condition(ConditionFieldEnum.CUSTOMER_TYPE, OperatorEnum.EQUALS, "Premium")],
        actions=[make_action(ActionTypeEnum.PERCENT_DISCOUNT, 10)],
    )
    rule2 = make_rule(
        "Bulk 5%", priority=20,
        conditions=[make_condition(ConditionFieldEnum.QUANTITY, OperatorEnum.GREATER_OR_EQUAL, "1")],
        actions=[make_action(ActionTypeEnum.PERCENT_DISCOUNT, 5)],
    )
    result, outcome = calculate_price(
        product=product, customer=customer, quantity=1, location=None,
        calculation_date=date.today(), rules=[rule1, rule2], promotion=None, tax_rate_percent=0,
    )
    assert len(outcome.matched) == 2
    assert result.rule_discount_total == 30  # 20 + 10


def test_exclusive_rule_stops_further_evaluation():
    product = make_product(price=100)
    rule1 = make_rule(
        "Exclusive VIP 50%", priority=1, exclusive=True,
        actions=[make_action(ActionTypeEnum.PERCENT_DISCOUNT, 50)],
    )
    rule2 = make_rule(
        "Extra 5%", priority=2,
        actions=[make_action(ActionTypeEnum.PERCENT_DISCOUNT, 5)],
    )
    result, outcome = calculate_price(
        product=product, customer=None, quantity=1, location=None,
        calculation_date=date.today(), rules=[rule1, rule2], promotion=None, tax_rate_percent=0,
    )
    assert len(outcome.matched) == 1
    assert result.rule_discount_total == 50
    assert outcome.non_matched[0].reason.startswith("Skipped")


def test_non_stackable_rule_applies_alone():
    product = make_product(price=100)
    rule1 = make_rule("First 10%", priority=1, actions=[make_action(ActionTypeEnum.PERCENT_DISCOUNT, 10)])
    rule2 = make_rule(
        "Non-stackable 20%", priority=2, stackable=False,
        actions=[make_action(ActionTypeEnum.PERCENT_DISCOUNT, 20)],
    )
    result, outcome = calculate_price(
        product=product, customer=None, quantity=1, location=None,
        calculation_date=date.today(), rules=[rule1, rule2], promotion=None, tax_rate_percent=0,
    )
    assert len(outcome.matched) == 1
    assert result.rule_discount_total == 10


def test_max_discount_action_cap():
    product = make_product(price=1000)
    rule = make_rule(
        "Capped 50%",
        actions=[make_action(ActionTypeEnum.PERCENT_DISCOUNT, 50, max_amount=100)],
    )
    result, _ = calculate_price(
        product=product, customer=None, quantity=1, location=None,
        calculation_date=date.today(), rules=[rule], promotion=None, tax_rate_percent=0,
    )
    assert result.rule_discount_total == 100  # capped, not 500


def test_global_max_total_discount_cap():
    product = make_product(price=100)
    rule1 = make_rule("A", actions=[make_action(ActionTypeEnum.PERCENT_DISCOUNT, 50)])
    rule2 = make_rule("B", actions=[make_action(ActionTypeEnum.PERCENT_DISCOUNT, 50)])
    result, _ = calculate_price(
        product=product, customer=None, quantity=1, location=None,
        calculation_date=date.today(), rules=[rule1, rule2], promotion=None, tax_rate_percent=0,
    )
    # settings.MAX_TOTAL_DISCOUNT_PERCENT defaults to 60% -> capped at 60
    assert result.rule_discount_total <= 60.01


def test_rule_outside_date_window_is_skipped():
    product = make_product(price=100)
    rule = make_rule(
        "Expired promo rule",
        start=datetime(2020, 1, 1), end=datetime(2020, 12, 31),
        actions=[make_action(ActionTypeEnum.PERCENT_DISCOUNT, 20)],
    )
    result, outcome = calculate_price(
        product=product, customer=None, quantity=1, location=None,
        calculation_date=date.today(), rules=[rule], promotion=None, tax_rate_percent=0,
    )
    assert result.rule_discount_total == 0
    assert outcome.non_matched[0].reason == "Outside active date window"


def test_promotion_code_percent_with_cap():
    product = make_product(price=500)
    promo = SimpleNamespace(
        code="SAVE20", discount_type=DiscountTypeEnum.PERCENT, discount_value=20,
        minimum_purchase=0, maximum_discount=50, start_date=None, expiry_date=None,
        usage_limit=None, usage_count=0, is_active=True,
    )
    result, _ = calculate_price(
        product=product, customer=None, quantity=1, location=None,
        calculation_date=date.today(), rules=[], promotion=promo, tax_rate_percent=0,
    )
    # 20% of 500 = 100, capped at 50
    assert result.promotion_discount == 50
    assert result.final_price == 450


def test_promotion_below_minimum_purchase_invalid():
    product = make_product(price=10)
    promo = SimpleNamespace(
        code="BIG50", discount_type=DiscountTypeEnum.FLAT, discount_value=50,
        minimum_purchase=100, maximum_discount=None, start_date=None, expiry_date=None,
        usage_limit=None, usage_count=0, is_active=True,
    )
    result, _ = calculate_price(
        product=product, customer=None, quantity=1, location=None,
        calculation_date=date.today(), rules=[], promotion=promo, tax_rate_percent=0,
    )
    assert result.promotion is not None
    assert result.promotion.valid is False
    assert result.promotion_discount == 0
