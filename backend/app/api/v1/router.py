from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    categories,
    customers,
    dashboard,
    pricing,
    pricing_rules,
    products,
    promotions,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(categories.router)
api_router.include_router(products.router)
api_router.include_router(customers.router)
api_router.include_router(pricing_rules.router)
api_router.include_router(promotions.router)
api_router.include_router(pricing.router)
api_router.include_router(dashboard.router)
