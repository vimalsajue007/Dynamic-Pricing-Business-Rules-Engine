"""
Optional demo-data seeder.
Run inside the backend container (or locally with the same DB config):
    python seed_data.py
Creates: an admin user, a couple of categories/products/customers,
a handful of pricing rules exercising different features, and one promo code.
"""
from datetime import datetime, timedelta

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.customer import Customer, CustomerTypeEnum
from app.models.pricing_rule import (
    ActionTypeEnum,
    ConditionFieldEnum,
    OperatorEnum,
    PricingRule,
    RuleAction,
    RuleCondition,
    RuleLogicEnum,
)
from app.models.product import Category, Product
from app.models.promotion import DiscountTypeEnum, Promotion
from app.models.user import RoleEnum, User


def run():
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == "admin@example.com").first():
            db.add(
                User(
                    full_name="System Admin",
                    email="admin@example.com",
                    hashed_password=hash_password("Admin@12345"),
                    role=RoleEnum.ADMIN,
                    is_active=True,
                )
            )

        electronics = db.query(Category).filter(Category.name == "Electronics").first()
        if not electronics:
            electronics = Category(name="Electronics", description="Gadgets and devices")
            db.add(electronics)
            db.flush()

        apparel = db.query(Category).filter(Category.name == "Apparel").first()
        if not apparel:
            apparel = Category(name="Apparel", description="Clothing and accessories")
            db.add(apparel)
            db.flush()

        if not db.query(Product).filter(Product.sku == "ELEC-001").first():
            db.add(Product(name="Wireless Headphones", sku="ELEC-001", base_price=99.99, category_id=electronics.id))
        if not db.query(Product).filter(Product.sku == "ELEC-002").first():
            db.add(Product(name="Smart Watch", sku="ELEC-002", base_price=199.99, category_id=electronics.id))
        if not db.query(Product).filter(Product.sku == "APP-001").first():
            db.add(Product(name="Cotton T-Shirt", sku="APP-001", base_price=19.99, category_id=apparel.id))

        if not db.query(Customer).filter(Customer.email == "priya@example.com").first():
            db.add(Customer(name="Priya Sharma", email="priya@example.com", customer_type=CustomerTypeEnum.PREMIUM, location="Chennai"))
        if not db.query(Customer).filter(Customer.email == "arjun@example.com").first():
            db.add(Customer(name="Arjun Kumar", email="arjun@example.com", customer_type=CustomerTypeEnum.WHOLESALE, location="Coimbatore"))

        db.flush()

        if not db.query(PricingRule).filter(PricingRule.name == "Premium Customer Discount").first():
            rule = PricingRule(
                name="Premium Customer Discount",
                description="10% off for Premium customers",
                priority=10,
                condition_logic=RuleLogicEnum.AND,
                is_stackable=True,
            )
            rule.conditions = [RuleCondition(field=ConditionFieldEnum.CUSTOMER_TYPE, operator=OperatorEnum.EQUALS, value="Premium")]
            rule.actions = [RuleAction(action_type=ActionTypeEnum.PERCENT_DISCOUNT, value=10)]
            db.add(rule)

        if not db.query(PricingRule).filter(PricingRule.name == "Bulk Quantity Discount").first():
            rule = PricingRule(
                name="Bulk Quantity Discount",
                description="5% off for 10 or more units",
                priority=20,
                is_stackable=True,
            )
            rule.conditions = [RuleCondition(field=ConditionFieldEnum.QUANTITY, operator=OperatorEnum.GREATER_OR_EQUAL, value="10")]
            rule.actions = [RuleAction(action_type=ActionTypeEnum.PERCENT_DISCOUNT, value=5)]
            db.add(rule)

        if not db.query(PricingRule).filter(PricingRule.name == "Electronics Bulk Bonus").first():
            rule = PricingRule(
                name="Electronics Bulk Bonus",
                description="8% off Electronics when buying 5+",
                priority=15,
                condition_logic=RuleLogicEnum.AND,
                is_stackable=True,
            )
            rule.conditions = [
                RuleCondition(field=ConditionFieldEnum.CATEGORY, operator=OperatorEnum.EQUALS, value="Electronics"),
                RuleCondition(field=ConditionFieldEnum.QUANTITY, operator=OperatorEnum.GREATER_OR_EQUAL, value="5"),
            ]
            rule.actions = [RuleAction(action_type=ActionTypeEnum.PERCENT_DISCOUNT, value=8, max_amount=200)]
            db.add(rule)

        if not db.query(Promotion).filter(Promotion.code == "WELCOME20").first():
            db.add(
                Promotion(
                    code="WELCOME20",
                    description="20% off, capped at $50, min purchase $30",
                    discount_type=DiscountTypeEnum.PERCENT,
                    discount_value=20,
                    minimum_purchase=30,
                    maximum_discount=50,
                    start_date=datetime.utcnow() - timedelta(days=1),
                    expiry_date=datetime.utcnow() + timedelta(days=90),
                    usage_limit=1000,
                )
            )

        db.commit()
        print("Seed data created successfully.")
        print("Admin login -> email: admin@example.com | password: Admin@12345")
    finally:
        db.close()


if __name__ == "__main__":
    run()
