"""Authentication, authorization envelope and security header tests."""
from tests.conftest import (
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    USER_PASSWORD,
    auth_headers,
    login,
    register_user,
    unique,
)


def test_health_and_readiness(client):
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"
    assert health.headers["x-content-type-options"] == "nosniff"
    assert health.headers["x-frame-options"] == "DENY"

    ready = client.get("/ready")
    assert ready.status_code == 200
    assert ready.json()["database"] == "connected"

    root = client.get("/")
    assert root.status_code == 200
    assert root.json()["docs"] == "/docs"

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "ai_safety_governance_up 1" in metrics.text


def test_register_and_login_returns_profile_and_roles(client):
    user = register_user(client)
    assert user["email"].endswith("@example.com")
    assert user["roles"] == []
    assert user["is_superuser"] is False
    assert "hashed_password" not in user

    auth = login(client, user["email"], USER_PASSWORD)
    assert auth["access_token"]
    assert auth["user"]["email"] == user["email"]

    me = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {auth['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["username"] == user["username"]


def test_register_rejects_duplicates_and_weak_passwords(client):
    user = register_user(client)

    duplicate = client.post(
        "/api/v1/auth/register",
        json={
            "username": user["username"],
            "email": f"other-{user['email']}",
            "password": USER_PASSWORD,
        },
    )
    assert duplicate.status_code == 400

    weak = client.post(
        "/api/v1/auth/register",
        json={"username": unique("weak"), "email": f"{unique('w')}@example.com", "password": "short"},
    )
    assert weak.status_code == 422

    invalid_username = client.post(
        "/api/v1/auth/register",
        json={
            "username": "bad user name!",
            "email": f"{unique('bad')}@example.com",
            "password": USER_PASSWORD,
        },
    )
    assert invalid_username.status_code == 422


def test_self_registration_cannot_create_superuser(client):
    user = register_user(client, superuser=True)
    assert user["is_superuser"] is False
    assert user["roles"] == []


def test_login_rejects_wrong_password_and_unknown_user(client):
    user = register_user(client)
    wrong = client.post(
        "/api/v1/auth/token",
        data={"username": user["email"], "password": "WrongPass123!"},
    )
    assert wrong.status_code == 401

    unknown = client.post(
        "/api/v1/auth/token",
        data={"username": "nobody@example.com", "password": USER_PASSWORD},
    )
    assert unknown.status_code == 401


def test_refresh_token_requires_the_correct_password(client):
    """Regression: refresh used to issue a token for any password."""
    user = register_user(client)
    bad = client.post(
        "/api/v1/auth/refresh-token",
        data={"username": user["email"], "password": "NotThePassword123!"},
    )
    assert bad.status_code == 401
    assert bad.json()["detail"] == "Invalid credentials"

    good = client.post(
        "/api/v1/auth/refresh-token",
        data={"username": user["email"], "password": USER_PASSWORD},
    )
    assert good.status_code == 200
    assert good.json()["access_token"]


def test_admin_login_grants_all_scopes(client):
    auth = login(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    assert auth["user"]["is_superuser"] is True
    assert "admin" in auth["user"]["roles"]

    for path in (
        "/api/v1/users/",
        "/api/v1/compliance/summary",
        "/api/v1/models/versions",
        "/api/v1/security/summary",
        "/api/v1/settings",
    ):
        response = client.get(
            path, headers={"Authorization": f"Bearer {auth['access_token']}"}
        )
        assert response.status_code == 200, f"{path}: {response.text}"


def test_protected_endpoints_require_a_token(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401

    response = client.get(
        "/api/v1/users/me", headers={"Authorization": "Bearer not-a-jwt"}
    )
    assert response.status_code == 401


def test_regular_user_cannot_access_admin_resources(client, user_headers):
    for path in (
        "/api/v1/users/",
        "/api/v1/compliance/summary",
        "/api/v1/models/versions",
        "/api/v1/security/summary",
        "/api/v1/settings",
    ):
        response = client.get(path, headers=user_headers)
        assert response.status_code == 403, f"{path}: {response.text}"


def test_regular_user_can_read_dashboard_and_monitoring(client, user_headers):
    for path in (
        "/api/v1/dashboard/summary",
        "/api/v1/monitoring/system",
        "/api/v1/monitoring/models/metrics",
        "/api/v1/monitoring/models/performance",
        "/api/v1/monitoring/resources/cpu",
        "/api/v1/monitoring/alerts",
    ):
        response = client.get(path, headers=user_headers)
        assert response.status_code == 200, f"{path}: {response.text}"


def test_cors_allows_configured_origin_only(client):
    allowed = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:5173"

    denied = client.options(
        "/health",
        headers={
            "Origin": "https://evil.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in denied.headers


def test_logout_is_idempotent(client):
    user = register_user(client)
    headers = auth_headers(client, user["email"], USER_PASSWORD)
    response = client.post("/api/v1/auth/logout", headers=headers)
    assert response.status_code == 200
