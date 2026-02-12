# tests/conftest.py
from datetime import datetime, timezone

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_async_db
from app.main import app
from app.models.newsletter import Newsletter
from app.models.organization import Organization
from app.models.users import User

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def override_get_db(db_session):
    app.dependency_overrides[get_async_db] = lambda: db_session


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def test_organization(db_session):
    org = Organization(
        name="Gammaedge",
        slug="gamma",
        email_domain="gammaedge.io",
        is_active=True,
        sender_name="rohit",
        sender_email="rohit.ankolnerkar@gammaedge.io",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    return org


@pytest_asyncio.fixture
async def test_user(db_session, test_organization):
    user = User(
        email="rohit.ankolnerkar@gammaedge.io",
        password_hash=hash_password("password123"),
        role="admin",
        organization_id=test_organization.id,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        last_login_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_newsletter(test_user, db_session: AsyncSession):

    newsletter = Newsletter(
        subject="Test Newsletter",
        content="Test content",
        organization_id=test_user.organization_id,
        status="draft",
    )
    db_session.add(newsletter)
    await db_session.commit()
    await db_session.refresh(newsletter)
    return newsletter
