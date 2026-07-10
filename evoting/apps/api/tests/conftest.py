"""Test fixtures: in-memory SQLite, memory chain, fake biometrics, ASGI client."""

from __future__ import annotations

import os

# Configure the environment BEFORE app modules read settings.
os.environ.update(
    {
        "DATA_ENCRYPTION_KEY": "test-encryption-key-000000000000",
        "JWT_SECRET": "test-jwt-secret-at-least-32-bytes-long-000",
        "CHAIN_BACKEND": "memory",
        "BIOMETRICS_BACKEND": "fake",
        "REDIS_URL": "",
        "CORS_ORIGINS": "http://localhost:3000",
        # Effectively disable rate limiting in tests.
        "RATE_LIMIT_LOGIN": "100000",
        "RATE_LIMIT_REGISTER": "100000",
        "RATE_LIMIT_VERIFICATION": "100000",
        "RATE_LIMIT_VOTE": "100000",
    }
)

from collections.abc import AsyncGenerator  # noqa: E402

import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.biometrics_client import FakeBiometricsClient, set_biometrics_client  # noqa: E402
from app.chain import set_chain_client  # noqa: E402
from app.chain.memory import MemoryChainClient  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.models import Admin  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import create_app  # noqa: E402
from app.seed.seed import seed_geo  # noqa: E402


@pytest_asyncio.fixture
async def sessionmaker_fixture() -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    yield maker
    await engine.dispose()


@pytest_asyncio.fixture
async def client(
    sessionmaker_fixture: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncClient, None]:
    # Fresh chain + biometrics + rate-limit/session state per test for isolation.
    set_chain_client(MemoryChainClient())
    set_biometrics_client(FakeBiometricsClient())
    import app.core.rate_limit as rl
    import app.core.sessions as ss

    rl._limiter = None
    ss._store = None

    # Seed geography and a bootstrap admin.
    async with sessionmaker_fixture() as db:
        await seed_geo(db)
        db.add(
            Admin(
                email="admin@evoting.com",
                password_hash=hash_password("admin12345"),
                full_name="Test Admin",
            )
        )
        await db.commit()

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with sessionmaker_fixture() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    set_chain_client(None)
    set_biometrics_client(None)


@pytest_asyncio.fixture
async def admin_token(client: AsyncClient) -> str:
    resp = await client.post(
        "/auth/admin/login",
        json={"email": "admin@evoting.com", "password": "admin12345"},
    )
    assert resp.status_code == 200, resp.text
    return str(resp.json()["access_token"])
