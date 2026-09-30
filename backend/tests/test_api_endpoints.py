"""
FastAPI Endpoints Verification Tests
"""

import pytest
from starlette.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in ["ok", "HEALTHY"]

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "Swasthya Records"
    assert data["tagline"] == "Predict. Prevent. Redistribute."

def test_list_facilities():
    response = client.get("/api/v1/facilities/")
    assert response.status_code == 200
    facilities = response.json()
    assert len(facilities) == 33
    
    # Filter by state
    response_bihar = client.get("/api/v1/facilities/?state_code=IN-BR")
    assert response_bihar.status_code == 200
    assert len(response_bihar.json()) > 0
    assert all(f["state_code"] == "IN-BR" for f in response_bihar.json())

def test_facility_hierarchy():
    response = client.get("/api/v1/facilities/geo/hierarchy")
    assert response.status_code == 200
    tree = response.json()
    assert "Bihar" in tree
    assert "Uttar Pradesh" in tree
    assert "Patna" in tree["Bihar"]

def test_phc_inventory_telemetry():
    response = client.get("/api/v1/operational/inventory/PHC-BR-PAT-001")
    assert response.status_code == 200
    data = response.json()
    assert data["phc_id"] == "PHC-BR-PAT-001"
    assert data["data_source"] == "SIMULATED"
    assert len(data["inventory"]) == 20

def test_bed_and_staffing_status():
    response_beds = client.get("/api/v1/operational/beds")
    assert response_beds.status_code == 200
    assert response_beds.json()["data_source"] == "SIMULATED"
    
    response_staff = client.get("/api/v1/operational/staffing")
    assert response_staff.status_code == 200
    assert response_staff.json()["data_source"] == "SIMULATED"

def test_emergency_trigger_and_clear():
    payload = {
        "event_type": "PATIENT_SURGE",
        "affected_district_ids": ["BR-PATNA", "UP-VARANASI"],
        "demand_multiplier": 1.40,
        "severity": "HIGH",
        "duration_days": 5,
        "description": "Test acute seasonal fever surge"
    }
    response = client.post("/api/v1/emergencies/trigger", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACTIVE"
    assert data["demand_multiplier"] == 1.40
    assert data["facilities_impacted_count"] > 0
    
    # List active
    response_active = client.get("/api/v1/emergencies/active")
    assert response_active.status_code == 200
    assert len(response_active.json()) >= 1
    
    # Clear
    response_clear = client.post("/api/v1/emergencies/clear")
    assert response_clear.status_code == 200
    assert response_clear.json()["status"] == "SUCCESS"

def test_simulation_status():
    response = client.get("/api/v1/simulation/status")
    assert response.status_code == 200
    data = response.json()
    assert data["is_running"] is True
    assert data["total_facilities_tracked"] == 33
    assert data["total_medicines_tracked"] == 20
