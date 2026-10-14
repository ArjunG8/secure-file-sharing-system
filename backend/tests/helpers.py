"""Test helpers (import as `from tests.helpers import ...`)."""

import uuid

from app.models import User


def make_user(role: str = "user") -> User:
    """An unsaved User object for dependency overrides in tests."""
    return User(
        id=uuid.uuid4(),
        email=f"{uuid.uuid4().hex[:8]}@example.test",
        username=f"user_{uuid.uuid4().hex[:8]}",
        password_hash="not-a-real-hash",
        role=role,
        is_active=True,
        failed_login_count=0,
    )
