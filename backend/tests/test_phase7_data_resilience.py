"""
Phase 7 Verification Tests: Data Integrity, Simulation Determinism, and AI Hallucination Guardrails
"""

import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.services.copilot_service import copilot_service

client = TestClient(app)

def test_deterministic_simulation_reset():
    """Verify simulation reset restores clean baseline without errors."""
    response = client.post("/api/v1/simulation/reset")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "reset to baseline" in data["message"]

def test_deterministic_demo_scenario_seed():
    """Verify demo seed triggers deterministic surge and provides exact metadata."""
    response = client.post("/api/v1/simulation/demo-seed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["scenario"] == "DEMO_DETERMINISTIC_SURGE"
    assert "Patna" in data["affected_region"]
    assert data["destination_facility"] == "PHC-BR-PAT-001"
    assert data["expected_before_risk"] == "CRITICAL"
    assert data["expected_after_risk"] == "LOW"

def test_ai_copilot_hallucination_guardrail():
    """
    Verify Gemini Copilot NEVER invents inventory for non-existent facilities.
    Querying a non-existent ID must return 'not found' or insufficient evidence,
    never fabricated stock numbers.
    """
    result = copilot_service.process_query(
        user_message="What is the current stock level of PHC-999999?",
        user_role="ADMIN",
        user_id="judge-evaluator"
    )
    assert "response" in result
    content = result["response"].lower()
    # Must indicate facility was not found or not in records
    assert any(phrase in content for phrase in [
        "not find", "could not find", "does not exist", "not found", "couldn't find", "no data", "unable to find", "not in registry"
    ])
    # Must NOT invent arbitrary thousands of units
    assert "5,000 units" not in content

def test_data_invariants_and_integrity():
    """Verify operational datasets satisfy all healthcare invariants: no negative inventory, valid beds."""
    fac_resp = client.get("/api/v1/facilities/")
    assert fac_resp.status_code == 200
    facilities = fac_resp.json()
    
    facility_ids = set()
    for f in facilities:
        # 1. Unique Facility IDs
        assert f["facility_id"] not in facility_ids, f"Duplicate facility ID: {f['facility_id']}"
        facility_ids.add(f["facility_id"])
        
        # 2. Non-negative bed count
        assert f["sanctioned_beds"] >= 0
        
        # 3. Valid geographic hierarchy (all official Indian state ISO codes start with IN-)
        assert f["state_code"].startswith("IN-")
        assert f["latitude"] > 0
        assert f["longitude"] > 0

    # 4. Inventory Telemetry Invariants
    inv_resp = client.get("/api/v1/operational/inventory/PHC-BR-PAT-001")
    assert inv_resp.status_code == 200
    inventory_items = inv_resp.json()["inventory"]
    for item in inventory_items:
        assert item.get("current_stock", item.get("closing_stock", 0)) >= 0, f"Negative stock detected: {item}"
        assert item.get("daily_consumption", 0) >= 0, f"Negative consumption detected: {item}"
        assert item.get("days_of_stock_available", item.get("days_of_supply", 0)) >= 0, f"Negative days of supply: {item}"

