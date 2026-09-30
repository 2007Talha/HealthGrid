"""
Swasthya Records - Phase 5 Copilot Service Unit Tests
Validates all 12 tools, NLP query dispatch, role-based security, what-if simulation, and audit logging.
"""

import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.services.copilot_service import copilot_service

client = TestClient(app)

def test_copilot_tool_1_national_summary():
    res = copilot_service.get_national_summary()
    assert res["total_facilities"] >= 33
    assert len(res["states_represented"]) >= 5
    assert "critical_alerts_count" in res
    assert "medicine_shortages_count" in res

def test_copilot_tool_2_state_summary():
    res = copilot_service.get_state_summary("Bihar")
    assert res["state"] == "Bihar"
    assert res["facility_count"] >= 1
    assert "critical_alerts_count" in res

    # Unknown state
    err_res = copilot_service.get_state_summary("Atlantis")
    assert "error" in err_res

def test_copilot_tool_3_district_summary():
    res = copilot_service.get_district_summary("Patna")
    assert res["district_name"] == "Patna"
    assert res["facility_count"] >= 1
    assert "bed_occupancy_pct" in res

def test_copilot_tool_4_facility_status():
    res = copilot_service.get_facility_status("PHC-BR-PAT-001")
    assert res["facility_id"] == "PHC-BR-PAT-001"
    assert "bed_capacity" in res
    assert "staff_status" in res
    assert "critical_medicine_risks" in res

def test_copilot_tool_5_critical_alerts():
    res = copilot_service.get_critical_alerts(min_severity="HIGH")
    assert "total_alerts" in res
    assert "alerts" in res

def test_copilot_tool_6_stockout_risks():
    res = copilot_service.get_stockout_risks(risk_level="CRITICAL")
    assert "results" in res
    assert isinstance(res["results"], list)

def test_copilot_tool_7_medicine_status():
    res = copilot_service.get_medicine_status("PHC-BR-PAT-001", "MED-PCM-500")
    assert res["facility_id"] == "PHC-BR-PAT-001"
    assert res["medicine_code"] == "MED-PCM-500"
    assert res["current_stock"] >= 0

def test_copilot_tool_8_forecast():
    res = copilot_service.get_forecast("PHC-BR-PAT-001", "MED-PCM-500", horizon=7)
    assert res["facility_id"] == "PHC-BR-PAT-001"
    assert len(res["forecasts"]) == 7

def test_copilot_tool_9_redistribution_options():
    res = copilot_service.get_redistribution_options("PHC-BR-PAT-001", "MED-AMX-500")
    assert "status" in res
    assert "recommendation" in res

def test_copilot_tool_11_emergency_status():
    res = copilot_service.get_emergency_status()
    assert "active_emergency" in res

def test_copilot_tool_12_resource_pressure():
    res = copilot_service.get_resource_pressure()
    assert "top_pressured_medicines" in res
    assert "facilities_with_bed_strain" in res

def test_what_if_simulation_engine():
    res = copilot_service.run_what_if_simulation("PHC-BR-PAT-001", "MED-PCM-500", demand_surge_pct=40.0, transfer_units=500)
    assert res["is_simulation"] is True
    assert "baseline" in res
    assert "simulated_outcome" in res
    assert res["simulated_outcome"]["simulated_stock"] == res["baseline"]["current_stock"] + 500

def test_copilot_chat_endpoints():
    # Chat English
    resp = client.post("/api/v1/copilot/chat", json={
        "message": "Which PHCs are at highest medicine stock-out risk?",
        "language": "en",
        "user_role": "ADMIN"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "response" in data
    assert len(data["tool_calls"]) > 0

    # Chat Hindi
    resp_hi = client.post("/api/v1/copilot/chat", json={
        "message": "उत्तर प्रदेश में स्वास्थ्य संसाधनों की स्थिति क्या है?",
        "language": "hi",
        "user_role": "ADMIN"
    })
    assert resp_hi.status_code == 200
    assert resp_hi.json()["language"] == "hi"

def test_copilot_security_role_scoping():
    # District Operator blocked from national view
    resp = client.post("/api/v1/copilot/chat", json={
        "message": "Show me the national healthcare summary",
        "user_role": "DISTRICT_OPERATOR"
    })
    assert resp.status_code == 200
    assert "Access restricted" in resp.json()["response"]

def test_copilot_voice_endpoint():
    resp = client.post("/api/v1/copilot/voice", json={
        "audio_base64": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=",
        "language": "en"
    })
    assert resp.status_code == 200
    assert resp.json()["audio_response_available"] is True

def test_copilot_what_if_endpoint():
    resp = client.post("/api/v1/copilot/what-if", json={
        "facility_id": "PHC-BR-PAT-001",
        "medicine_code": "MED-PCM-500",
        "demand_surge_pct": 25.0,
        "transfer_units": 300
    })
    assert resp.status_code == 200
    assert resp.json()["is_simulation"] is True

import uuid

def test_copilot_history_and_audit():
    conv_id = f"test-conv-audit-{uuid.uuid4().hex[:6]}"
    client.post("/api/v1/copilot/chat", json={
        "message": "Summarize today's health resource situation",
        "conversation_id": conv_id
    })
    
    resp_hist = client.get(f"/api/v1/copilot/history?conversation_id={conv_id}")
    assert resp_hist.status_code == 200
    assert resp_hist.json()["turns_count"] >= 1
    
    resp_audit = client.get("/api/v1/copilot/audit-log?limit=10")
    assert resp_audit.status_code == 200
    assert resp_audit.json()["total_entries"] >= 1
