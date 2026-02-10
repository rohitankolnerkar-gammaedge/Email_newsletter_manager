from __future__ import with_statement

import os
from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context

# -------------------------------------------------
# Path & env setup (NO executable code before imports)
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
os.sys.path.append(str(BASE_DIR))

load_dotenv()

# -------------------------------------------------
# Alembic Config
# -------------------------------------------------
config = context.config

# -------------------------------------------------
# Logging
# -------------------------------------------------
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -------------------------------------------------
# Database URL
# -------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL_SYNC")
if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL_SYNC not set in .env")

# -------------------------------------------------
# Models (for autogenerate)
# -------------------------------------------------
from app.db.base import Base  # noqa: E402

target_metadata = Base.metadata


# -------------------------------------------------
# Offline migrations
# -------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# -------------------------------------------------
# Online migrations
# -------------------------------------------------
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        {},
        url=DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# -------------------------------------------------
# Entry point
# -------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
