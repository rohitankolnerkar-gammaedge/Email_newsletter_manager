import os
import sys

# Make app importable for Alembic migrations
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from app.db.base import Base  # noqa: E402

# Alembic Config object
config = context.config  # type: ignore

# Interpret the config file for Python logging
fileConfig(config.config_file_name)  # type: ignore

# Metadata for 'autogenerate' support
target_metadata = Base.metadata  # type: ignore

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL_SYNC", config.get_main_option("sqlalchemy.url"))  # type: ignore


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        {"sqlalchemy.url": DATABASE_URL}, poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
