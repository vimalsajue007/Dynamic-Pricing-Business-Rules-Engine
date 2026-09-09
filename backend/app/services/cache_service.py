from app.core.redis_client import cache_delete_prefix

PRODUCT_PREFIX = "products:"
RULE_PREFIX = "rules:"
PROMO_PREFIX = "promotions:"
DASHBOARD_PREFIX = "dashboard:"


def invalidate_products():
    cache_delete_prefix(PRODUCT_PREFIX)
    cache_delete_prefix(DASHBOARD_PREFIX)


def invalidate_rules():
    cache_delete_prefix(RULE_PREFIX)
    cache_delete_prefix(DASHBOARD_PREFIX)


def invalidate_promotions():
    cache_delete_prefix(PROMO_PREFIX)
    cache_delete_prefix(DASHBOARD_PREFIX)


def invalidate_dashboard():
    cache_delete_prefix(DASHBOARD_PREFIX)
