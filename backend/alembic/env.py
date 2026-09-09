from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.core.config import settings
from app.core.database import Base
# Import all models so they register on Base.metadata
from app.models import customer, pricing_calculation, pricing_rule, product, promotion, user  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# NOTE: we intentionally do NOT call config.set_main_option("sqlalchemy.url", ...)
# or engine_from_config(). Both round-trip the URL through configparser, which
# treats `%` as interpolation syntax — a password containing `%40` (an encoded
# `@`, `#`, etc.) will crash with "invalid interpolation syntax". Building the
# engine directly from settings.SQLALCHEMY_DATABASE_URI sidesteps that entirely.


def run_migrations_offline() -> None:
    context.configure(
        url=settings.SQLALCHEMY_DATABASE_URI,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(settings.SQLALCHEMY_DATABASE_URI, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()