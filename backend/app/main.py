import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import configure_logging

configure_logging(logging.INFO if not settings.DEBUG else logging.DEBUG)
logger = logging.getLogger("pricing_engine")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "A reusable, configurable dynamic pricing and business-rules engine. "
        "Pricing conditions live in the database, not in route handlers — "
        "administrators can add/change rules without redeploying code."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Health"])
def root():
    return {"success": True, "message": f"{settings.PROJECT_NAME} is running", "data": {"docs": "/docs"}}


@app.get("/health", tags=["Health"])
def health_check():
    return {"success": True, "message": "healthy", "data": None}


@app.on_event("startup")
def on_startup():
    logger.info("%s starting up (env=%s)", settings.PROJECT_NAME, settings.ENVIRONMENT)
