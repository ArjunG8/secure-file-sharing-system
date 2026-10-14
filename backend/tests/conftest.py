"""Shared fixtures. Secrets are generated randomly per test run - never hardcoded.

By default tests use in-memory SQLite. Set TEST_DATABASE_URL to run against PostgreSQL.
"""

import base64
import os
import secrets
from collections.abc import Iterator

# Configure the environment BEFORE any app module reads settings.
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ["JWT_SECRET_KEY"] = secrets.token_urlsafe(48)
os.environ["MASTER_KEY_ENCRYPTION_KEY"] = base64.b64encode(os.urandom(32)).decode()
os.environ["AUDIT_HMAC_KEY"] = base64.b64encode(os.urandom(32)).decode()
os.environ["LLM_PROVIDER"] = "disabled"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.database import get_engine, get_sessionmaker  # noqa: E402
from app.main import create_app  # noqa: E402
from app.models import Base  # noqa: E402

get_settings.cache_clear()
get_engine.cache_clear()
get_sessionmaker.cache_clear()


@pytest.fixture(scope="session", autouse=True)
def _schema() -> Iterator[None]:
    engine = get_engine()
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db() -> Iterator[Session]:
    session = get_sessionmaker()()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app) -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c
