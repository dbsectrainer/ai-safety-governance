"""Model, compliance, monitoring, dashboard and settings integration tests."""
from tests.conftest import unique


def test_model_version_lifecycle_and_monitoring(client, admin_headers):
    name = unique("model")
    payload = {
        "name": name,
        "version": "1.0.0",
        "version_metadata": {"framework": "sklearn"},
        "status": "deployed",
    }
    created = client.post("/api/v1/models/versions", headers=admin_headers, json=payload)
    assert created.status_code == 201, created.text
    version = created.json()
    assert version["name"] == name

    duplicate = client.post("/api/v1/models/versions", headers=admin_headers, json=payload)
    assert duplicate.status_code == 409

    listing = client.get("/api/v1/models/versions", headers=admin_headers)
    assert listing.status_code == 200
    assert any(item["id"] == version["id"] for item in listing.json())

    log = client.post(
        "/api/v1/models/monitoring",
        headers=admin_headers,
        json={
            "version_id": version["id"],
            "metric_name": "accuracy",
            "metric_value": {"value": 0.93},
        },
    )
    assert log.status_code == 201, log.text

    performance = client.get("/api/v1/monitoring/models/performance", headers=admin_headers)
    assert performance.status_code == 200
    observed = next(item for item in performance.json() if item["modelId"] == str(version["id"]))
    assert observed["metrics"]["accuracy"] == 0.93
    assert observed["status"] in {"healthy", "degraded", "error"}

    updated = client.put(
        f"/api/v1/models/versions/{version['id']}",
        headers=admin_headers,
        json={"status": "retired"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "retired"

    deleted = client.delete(f"/api/v1/models/versions/{version['id']}", headers=admin_headers)
    assert deleted.status_code == 200
    assert client.get(
        f"/api/v1/models/versions/{version['id']}", headers=admin_headers
    ).status_code == 404


def test_regular_user_cannot_create_model_versions(client, user_headers):
    response = client.post(
        "/api/v1/models/versions",
        headers=user_headers,
        json={
            "name": unique("forbidden"),
            "version": "1.0.0",
            "version_metadata": {},
            "status": "registered",
        },
    )
    assert response.status_code == 403


def test_compliance_checks_run_and_persist_records(client, admin_headers):
    run = client.post("/api/v1/compliance/checks/run", headers=admin_headers)
    assert run.status_code == 200, run.text
    body = run.json()
    assert body["summary"]["total_rules"] == 3
    assert body["summary"]["compliant_rules"] == 3
    assert body["summary"]["score"] == 100
    assert body["report"].startswith("compliance_report_")
    assert len(body["records"]) == 3

    summary = client.get("/api/v1/compliance/summary", headers=admin_headers)
    assert summary.status_code == 200
    summary_body = summary.json()
    assert summary_body["score"] == 100
    assert summary_body["total_regulations"] == 3
    assert summary_body["status_counts"]["compliant"] == 3
    assert summary_body["last_run"] is not None

    records = client.get("/api/v1/compliance/records", headers=admin_headers)
    assert records.status_code == 200
    assert len(records.json()) >= 3

    logs = client.get("/api/v1/compliance/audit-logs", headers=admin_headers)
    assert logs.status_code == 200
    assert any(entry["action"] == "run_checks" for entry in logs.json())


def test_compliance_record_crud(client, admin_headers):
    created = client.post(
        "/api/v1/compliance/records",
        headers=admin_headers,
        json={
            "regulation_type": "Test Framework",
            "status": "needs_review",
            "details": {"owner": "qa"},
        },
    )
    assert created.status_code == 201, created.text
    record = created.json()
    assert record["status"] == "needs_review"

    record_id = record["id"]
    updated = client.put(
        f"/api/v1/compliance/records/{record_id}",
        headers=admin_headers,
        json={"status": "compliant"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "compliant"

    deleted = client.delete(
        f"/api/v1/compliance/records/{record_id}", headers=admin_headers
    )
    assert deleted.status_code == 200
    assert client.get(
        f"/api/v1/compliance/records/{record_id}", headers=admin_headers
    ).status_code == 404


def test_monitoring_system_endpoints(client, user_headers):
    system = client.get("/api/v1/monitoring/system", headers=user_headers)
    assert system.status_code == 200
    body = system.json()
    assert {"cpu", "memory", "storage", "network"} <= set(body)
    assert all(0 <= body[key] <= 100 for key in body)

    cpu = client.get("/api/v1/monitoring/resources/cpu", headers=user_headers)
    assert cpu.status_code == 200
    assert isinstance(cpu.json(), list)
    if cpu.json():
        assert {"timestamp", "value"} <= set(cpu.json()[0])

    unknown = client.get("/api/v1/monitoring/resources/gpu", headers=user_headers)
    assert unknown.status_code == 404

    metrics = client.get("/api/v1/monitoring/models/metrics", headers=user_headers)
    assert metrics.status_code == 200
    assert "activeModels" in metrics.json()


def test_dashboard_summary_and_settings(client, admin_headers, user_headers):
    dashboard = client.get("/api/v1/dashboard/summary", headers=user_headers)
    assert dashboard.status_code == 200
    body = dashboard.json()
    assert {"active_users", "active_models", "compliance_score", "system_health"} <= set(
        body["metrics"]
    )
    assert len(body["performance"]) == 13
    assert isinstance(body["activity"], list)

    defaults = client.get("/api/v1/settings", headers=admin_headers)
    assert defaults.status_code == 200
    assert defaults.json()["settings"]["general"]["platform_name"]

    updated = client.put(
        "/api/v1/settings",
        headers=admin_headers,
        json={"general": {"debug_mode": True, "data_retention_days": 45}},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["settings"]["general"]["debug_mode"] is True
    assert updated.json()["settings"]["general"]["data_retention_days"] == 45

    persisted = client.get("/api/v1/settings", headers=admin_headers)
    assert persisted.json()["settings"]["general"]["data_retention_days"] == 45

    invalid = client.put(
        "/api/v1/settings",
        headers=admin_headers,
        json={"general": {"environment": "not-an-environment"}},
    )
    assert invalid.status_code == 422

    unknown = client.put(
        "/api/v1/settings",
        headers=admin_headers,
        json={"general": {"secret_token": "nope"}},
    )
    assert unknown.status_code == 422


def test_security_summary(client, admin_headers):
    response = client.get("/api/v1/security/summary", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["score"] <= 100
    assert body["checks"]
    assert body["recommendations"]
    assert body["metrics"]["security_score"] == body["score"]
