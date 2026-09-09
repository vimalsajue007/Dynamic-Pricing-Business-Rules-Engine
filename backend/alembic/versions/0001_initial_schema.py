"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(150), nullable=False, unique=True, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("ADMIN", "USER", name="roleenum"), nullable=False, server_default="USER"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "products",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String(200), nullable=False, index=True),
        sa.Column("sku", sa.String(64), nullable=False, unique=True, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("base_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("category_id", sa.Integer, sa.ForeignKey("categories.id"), nullable=True, index=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true(), index=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "customers",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String(150), nullable=False, index=True),
        sa.Column("email", sa.String(150), nullable=False, unique=True, index=True),
        sa.Column(
            "customer_type",
            sa.Enum("REGULAR", "PREMIUM", "BUSINESS", "WHOLESALE", name="customertypeenum"),
            nullable=False,
            server_default="REGULAR",
            index=True,
        ),
        sa.Column("location", sa.String(120), nullable=True, index=True),
        sa.Column("category", sa.String(120), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "pricing_rules",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String(150), nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("priority", sa.Integer, nullable=False, server_default="100", index=True),
        sa.Column("condition_logic", sa.Enum("AND", "OR", name="rulelogicenum"), nullable=False, server_default="AND"),
        sa.Column("is_exclusive", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("is_stackable", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("start_date", sa.DateTime, nullable=True),
        sa.Column("end_date", sa.DateTime, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true(), index=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "rule_conditions",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("rule_id", sa.Integer, sa.ForeignKey("pricing_rules.id"), nullable=False, index=True),
        sa.Column(
            "field",
            sa.Enum(
                "CUSTOMER_TYPE", "QUANTITY", "LOCATION", "CATEGORY", "PRODUCT", "ORDER_TOTAL", "DATE",
                name="conditionfieldenum",
            ),
            nullable=False,
        ),
        sa.Column(
            "operator",
            sa.Enum(
                "EQUALS", "NOT_EQUALS", "GREATER_THAN", "GREATER_OR_EQUAL", "LESS_THAN", "LESS_OR_EQUAL", "IN",
                name="operatorenum",
            ),
            nullable=False,
        ),
        sa.Column("value", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "rule_actions",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("rule_id", sa.Integer, sa.ForeignKey("pricing_rules.id"), nullable=False, index=True),
        sa.Column(
            "action_type",
            sa.Enum(
                "PERCENT_DISCOUNT", "FLAT_DISCOUNT", "SURCHARGE_PERCENT", "SURCHARGE_FLAT", "FIXED_PRICE",
                name="actiontypeenum",
            ),
            nullable=False,
        ),
        sa.Column("value", sa.Float, nullable=False),
        sa.Column("max_amount", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "promotions",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True, index=True),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("discount_type", sa.Enum("PERCENT", "FLAT", name="discounttypeenum"), nullable=False),
        sa.Column("discount_value", sa.Float, nullable=False),
        sa.Column("minimum_purchase", sa.Float, nullable=False, server_default="0"),
        sa.Column("maximum_discount", sa.Float, nullable=True),
        sa.Column("start_date", sa.DateTime, nullable=True),
        sa.Column("expiry_date", sa.DateTime, nullable=True),
        sa.Column("usage_limit", sa.Integer, nullable=True),
        sa.Column("usage_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true(), index=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "pricing_calculations",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), nullable=False, index=True),
        sa.Column("customer_id", sa.Integer, sa.ForeignKey("customers.id"), nullable=True, index=True),
        sa.Column("input_parameters", sa.JSON, nullable=False),
        sa.Column("applied_rules", sa.JSON, nullable=False),
        sa.Column("promo_code", sa.String(50), nullable=True),
        sa.Column("original_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("tax_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("final_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("calculation_time", sa.DateTime, server_default=sa.func.now(), index=True),
    )

    op.create_table(
        "calculation_rules",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("calculation_id", sa.Integer, sa.ForeignKey("pricing_calculations.id"), nullable=False, index=True),
        sa.Column("rule_id", sa.Integer, sa.ForeignKey("pricing_rules.id"), nullable=True, index=True),
        sa.Column("rule_name", sa.String(150), nullable=False),
        sa.Column("discount_applied", sa.Numeric(12, 2), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("calculation_rules")
    op.drop_table("pricing_calculations")
    op.drop_table("promotions")
    op.drop_table("rule_actions")
    op.drop_table("rule_conditions")
    op.drop_table("pricing_rules")
    op.drop_table("customers")
    op.drop_table("products")
    op.drop_table("categories")
    op.drop_table("users")
