"""Shared pytest fixtures for API integration tests.

The environment must be configured before ``src.main`` is imported because the
database engine is created at import time.
"""
import atexit
import os
import shutil
import tempfile
import uuid

import pytest

TEST_DIR = tempfile.mkdtemp(prefix="ai-safety-tests-")
atexit.register(shutil.rmtree, TEST_DIR, True)

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DIR}/test.db"
os.environ["SECRET_KEY"] = "test-only-secret-key-not-for-production"
os.environ["CORS_ORIGINS"] = "http://localhost:5173,http://127.0.0.1:5173"
os.environ["ADMIN_EMAIL"] = "admin@example.com"
os.environ["ADMIN_PASSWORD"] = "AdminPass123!"
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_FULL_NAME"] = "Test Administrator"
os.environ["COMPLIANCE_AUDIT_DIR"] = os.path.join(TEST_DIR, "compliance_logs")
os.environ["DB_AUTO_INIT"] = "true"

from fastapi.testclient import TestClient  # noqa: E402

from src.main import app  # noqa: E402

ADMIN_EMAIL = os.environ["ADMIN_EMAIL"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]
USER_PASSWORD = "UserPass123!"


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


def unique(prefix: str = "user") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


def register_user(client: TestClient, *, superuser: bool = False) -> dict:
    suffix = uuid.uuid4().hex[:8]
    username = f"user{suffix}"
    email = f"{username}@example.com"
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": USER_PASSWORD,
            "full_name": "Test User",
            "is_superuser": superuser,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def login(client: TestClient, username: str, password: str) -> dict:
    response = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()


def auth_headers(client: TestClient, username: str, password: str) -> dict:
    token = login(client, username, password)["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client):
    return auth_headers(client, ADMIN_EMAIL, ADMIN_PASSWORD)


@pytest.fixture
def regular_user(client):
    return register_user(client)


@pytest.fixture
def user_headers(client, regular_user):
    return auth_headers(client, regular_user["email"], USER_PASSWORD)
