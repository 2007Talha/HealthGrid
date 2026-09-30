"""
Phase 7 Verification Tests: RBAC Authentication, Regional Scoping, Rate Limiting & Health Checks
"""

import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.core.rate_limit import limiter

client = TestClient(app)

def test_health_check_ok():
    """Verify /health returns status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["code"] == 200

def test_health_dependencies():
    """Verify /health/dependencies checks all core subsystems."""
    response = client.get("/health/dependencies")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "subsystems" in data
    assert "database" in data["subsystems"]
    assert "bigquery" in data["subsystems"]
    assert "gemini_ai" in data["subsystems"]
    assert "simulation_engine" in data["subsystems"]

def test_request_id_tracing_header():
    """Verify structured logging middleware injects X-Request-ID header."""
    response = client.get("/health")
    assert "x-request-id" in response.headers
    assert len(response.headers["x-request-id"]) > 0

def test_admin_full_access():
    """Verify ADMIN role has full cross-state and cross-district access."""
    headers = {"X-User-Role": "ADMIN", "X-User-Id": "usr-admin-national"}
    # Access Bihar
    resp_br = client.get("/api/v1/facilities/?state_code=IN-BR", headers=headers)
    assert resp_br.status_code == 200
    # Access UP
    resp_up = client.get("/api/v1/facilities/?state_code=IN-UP", headers=headers)
    assert resp_up.status_code == 200

def test_state_operator_scoped_access_and_rejection():
    """Verify STATE_OPERATOR can access assigned state but is rejected (403) from accessing another state."""
    headers = {
        "X-User-Role": "STATE_OPERATOR",
        "X-User-Region": "Bihar (IN-BR)",
        "X-User-Id": "usr-state-bihar"
    }
    # Authorized access to assigned state (IN-BR)
    resp_valid = client.get("/api/v1/facilities/?state_code=IN-BR", headers=headers)
    assert resp_valid.status_code == 200
    assert all(f["state_code"] == "IN-BR" for f in resp_valid.json())

    # Unauthorized access to different state (IN-UP) -> MUST BE 403 FORBIDDEN
    resp_forbidden = client.get("/api/v1/facilities/?state_code=IN-UP", headers=headers)
    assert resp_forbidden.status_code == 403
    assert "Forbidden" in resp_forbidden.json()["detail"]

def test_district_operator_scoped_access_and_rejection():
    """Verify DISTRICT_OPERATOR can access assigned district but is rejected (403) from another district."""
    headers = {
        "X-User-Role": "DISTRICT_OPERATOR",
        "X-User-Region": "Patna District",
        "X-User-Id": "usr-dist-patna"
    }
    # Authorized access to assigned district (BR-PATNA)
    resp_valid = client.get("/api/v1/facilities/?district_code=BR-PATNA", headers=headers)
    assert resp_valid.status_code == 200

    # Unauthorized access to Lucknow district (UP-LUCKNOW) -> MUST BE 403 FORBIDDEN
    resp_forbidden = client.get("/api/v1/facilities/?district_code=UP-LUCKNOW", headers=headers)
    assert resp_forbidden.status_code == 403
    assert "Forbidden" in resp_forbidden.json()["detail"]

def test_invalid_role_rejection():
    """Verify invalid or unauthorized roles are rejected."""
    headers = {"X-User-Role": "INVALID_HACKER_ROLE"}
    resp = client.get("/api/v1/facilities/", headers=headers)
    assert resp.status_code in [401, 403]

def test_rate_limiting_enforcement():
    """Verify expensive endpoints return 429 Too Many Requests when rate limit is exceeded."""
    # Temporarily set limit to 2 requests for testing
    original_limit = limiter.limit
    limiter.limit = 2
    limiter.requests.clear()

    try:
        # First 2 requests succeed or return expected status
        payload = {"facility_id": "PHC-BR-PAT-001", "medicine_code": "MED-PCM-500", "demand_surge_pct": 10.0}
        resp1 = client.post("/api/v1/copilot/what-if", json=payload)
        resp2 = client.post("/api/v1/copilot/what-if", json=payload)
        assert resp1.status_code != 429
        assert resp2.status_code != 429

        # 3rd request should hit rate limit (429)
        resp3 = client.post("/api/v1/copilot/what-if", json=payload)
        assert resp3.status_code == 429
        assert "Rate limit exceeded" in resp3.json()["detail"]
        assert "retry-after" in resp3.headers
    finally:
        limiter.limit = original_limit
        limiter.requests.clear()
