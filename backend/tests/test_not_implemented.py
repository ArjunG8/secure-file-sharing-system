"""Unimplemented endpoints must answer an honest 501, attributed to the right module.

WHEN YOU IMPLEMENT AN ENDPOINT: delete its row from STUBBED_ENDPOINTS and add
real tests in tests/modules/. test_implemented_flags_are_honest enforces that a
module is not marked implemented while any of its endpoints are still stubbed.
"""

import uuid

import pytest

from app.api.deps import get_current_user
from app.core.modules import all_modules
from tests.helpers import make_user

FID = str(uuid.uuid4())
LATER = {"since": "2026-01-01T00:00:00Z", "until": "2026-01-02T00:00:00Z"}

# (module code, method, path, request kwargs)
STUBBED_ENDPOINTS = [
    ("M1", "post", "/api/v1/auth/register",
     {"json": {"email": "a@example.com", "username": "alice", "password": "x" * 12}}),
    ("M1", "post", "/api/v1/auth/login", {"json": {"email": "a@example.com", "password": "x"}}),
    ("M1", "post", "/api/v1/auth/refresh", {}),
    ("M1", "post", "/api/v1/auth/logout", {}),
    ("M1", "post", "/api/v1/auth/change-password",
     {"json": {"current_password": "x", "new_password": "y" * 12}}),
    ("M2", "post", "/api/v1/files", {"files": {"file": ("a.txt", b"hello", "text/plain")}}),
    ("M2", "get", "/api/v1/files", {}),
    ("M2", "get", f"/api/v1/files/{FID}", {}),
    ("M2", "get", f"/api/v1/files/{FID}/download", {}),
    ("M2", "delete", f"/api/v1/files/{FID}", {}),
    ("M3", "get", "/api/v1/keys/me", {}),
    ("M3", "post", "/api/v1/keys/rotate", {"json": {"purpose": "signing"}}),
    ("M3", "get", f"/api/v1/keys/users/{FID}/public", {}),
    ("M4", "get", f"/api/v1/signatures/files/{FID}", {}),
    ("M4", "post", f"/api/v1/signatures/files/{FID}/verify", {}),
    ("M5", "post", "/api/v1/shares", {"json": {"file_id": FID, "recipient_email": "b@example.com"}}),
    ("M5", "get", "/api/v1/shares/outgoing", {}),
    ("M5", "get", "/api/v1/shares/incoming", {}),
    ("M5", "delete", f"/api/v1/shares/{FID}", {}),
    ("M6", "get", "/api/v1/audit/logs", {}),
    ("M6", "get", "/api/v1/audit/verify", {}),
    ("M7", "post", "/api/v1/anomaly/train", {"json": {}}),
    ("M7", "post", "/api/v1/anomaly/score", {"json": {}}),
    ("M7", "get", "/api/v1/anomaly/detections", {}),
    ("M8", "post", "/api/v1/analysis", {"json": LATER}),
    ("M8", "get", "/api/v1/analysis", {}),
    ("M8", "get", f"/api/v1/analysis/{FID}", {}),
    ("M9", "post", f"/api/v1/verification/files/{FID}", {}),
    ("M9", "post", "/api/v1/verification/audit-chain", {}),
    ("M9", "get", "/api/v1/verification/runs", {}),
    ("M10", "get", "/api/v1/transport/status", {}),
]


@pytest.fixture
def admin_client(app, client):
    # Bypass M1 so each endpoint reaches its own module's code.
    app.dependency_overrides[get_current_user] = lambda: make_user(role="admin")
    yield client
    app.dependency_overrides.clear()


@pytest.mark.parametrize(
    ("module", "method", "path", "kwargs"),
    STUBBED_ENDPOINTS,
    ids=[f"{m}-{verb.upper()} {p}" for m, verb, p, _ in STUBBED_ENDPOINTS],
)
def test_stub_returns_honest_501(admin_client, module, method, path, kwargs):
    r = admin_client.request(method.upper(), path, **kwargs)
    assert r.status_code == 501, r.text
    error = r.json()["error"]
    assert error["code"] == "not_implemented"
    assert error["module"] == module


def test_protected_endpoints_do_not_bypass_auth(client):
    """Without the override, the M1 auth dependency runs (currently: honest 501)."""
    r = client.get("/api/v1/files")
    assert r.status_code in (401, 501)
    assert r.status_code != 200


def test_implemented_flags_are_honest():
    stubbed_modules = {module for module, *_ in STUBBED_ENDPOINTS}
    for info in all_modules():
        if info.implemented:
            assert info.code not in stubbed_modules, (
                f"{info.code} is marked implemented but still has stubbed endpoints"
            )
