from typing import cast

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import DATABASE_URL

engine = create_async_engine(
    cast(str, DATABASE_URL),
    echo=True,
    pool_pre_ping=True,
    connect_args={
        "statement_cache_size": 0,
    },
)


SessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, autoflush=False, autocommit=False
)


async def get_async_db():
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
