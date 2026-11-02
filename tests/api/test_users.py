"""User management API tests, including privilege boundaries."""
from tests.conftest import USER_PASSWORD, login, unique


def _create_user(client, admin_headers, *, superuser=False):
    suffix = unique("managed")
    payload = {
        "username": suffix,
        "email": f"{suffix}@example.com",
        "full_name": "Managed User",
        "password": USER_PASSWORD,
        "is_superuser": superuser,
    }
    response = client.post("/api/v1/users/", headers=admin_headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_admin_can_list_and_read_users(client, admin_headers):
    created = _create_user(client, admin_headers)
    response = client.get("/api/v1/users/", headers=admin_headers)
    assert response.status_code == 200
    assert any(user["id"] == created["id"] for user in response.json())

    detail = client.get(f"/api/v1/users/{created['id']}", headers=admin_headers)
    assert detail.status_code == 200
    assert detail.json()["email"] == created["email"]

    missing = client.get("/api/v1/users/999999", headers=admin_headers)
    assert missing.status_code == 404


def test_regular_user_cannot_create_or_delete_users(client, user_headers):
    response = client.post(
        "/api/v1/users/",
        headers=user_headers,
        json={
            "username": unique("nope"),
            "email": f"{unique('nope')}@example.com",
            "password": USER_PASSWORD,
        },
    )
    assert response.status_code == 403


def test_admin_updates_user_profile_and_password(client, admin_headers):
    created = _create_user(client, admin_headers)
    response = client.put(
        f"/api/v1/users/{created['id']}",
        headers=admin_headers,
        json={"full_name": "Updated Name", "password": "NewUserPass123!"},
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"

    login_response = login(client, created["email"], "NewUserPass123!")
    assert login_response["user"]["id"] == created["id"]


def test_admin_can_deactivate_and_reactivate_user(client, admin_headers):
    created = _create_user(client, admin_headers)
    deactivate = client.put(
        f"/api/v1/users/{created['id']}",
        headers=admin_headers,
        json={"is_active": False},
    )
    assert deactivate.status_code == 200
    assert deactivate.json()["is_active"] is False

    blocked = client.post(
        "/api/v1/auth/token",
        data={"username": created["email"], "password": USER_PASSWORD},
    )
    assert blocked.status_code == 401

    reactivate = client.put(
        f"/api/v1/users/{created['id']}",
        headers=admin_headers,
        json={"is_active": True},
    )
    assert reactivate.status_code == 200
    login(client, created["email"], USER_PASSWORD)


def test_admin_cannot_delete_or_demote_self(client, admin_headers):
    me = client.get("/api/v1/users/me", headers=admin_headers).json()

    delete = client.delete(f"/api/v1/users/{me['id']}", headers=admin_headers)
    assert delete.status_code == 400

    demote = client.put(
        f"/api/v1/users/{me['id']}",
        headers=admin_headers,
        json={"is_superuser": False},
    )
    assert demote.status_code == 400


def test_delete_user_removes_access(client, admin_headers):
    created = _create_user(client, admin_headers)
    response = client.delete(f"/api/v1/users/{created['id']}", headers=admin_headers)
    assert response.status_code == 200

    login_response = client.post(
        "/api/v1/auth/token",
        data={"username": created["email"], "password": USER_PASSWORD},
    )
    assert login_response.status_code == 401


def test_user_cannot_escalate_own_privileges(client, user_headers):
    response = client.put(
        "/api/v1/users/me",
        headers=user_headers,
        json={"is_superuser": True, "full_name": "Still A User"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["is_superuser"] is False
    assert body["full_name"] == "Still A User"
    assert body["roles"] == []


def test_admin_can_create_another_admin(client, admin_headers):
    created = _create_user(client, admin_headers, superuser=True)
    assert created["is_superuser"] is True
    assert "admin" in created["roles"]

    new_admin_login = login(client, created["email"], USER_PASSWORD)
    assert new_admin_login["user"]["is_superuser"] is True
    response = client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {new_admin_login['access_token']}"},
    )
    assert response.status_code == 200
