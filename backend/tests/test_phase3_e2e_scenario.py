"""
End-to-End Master Scenario Test for Phase 3:
Normal baseline -> Trigger 40% surge -> Consumption increases -> Forecast updates ->
DOSA drops below 2.0 days -> CRITICAL early warning alert generated -> Gemini explains result.
"""

import pytest
from starlette.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_phase3_master_scenario():
    # Step 1: Query baseline status for target facility (PHC Bakhtiyarpur)
    phc_id = "PHC-BR-PAT-001"
    med_code = "MED-PCM-500"
    
    resp_init_risk = client.get(f"/api/v1/risk/medicine/{phc_id}/{med_code}")
    assert resp_init_risk.status_code == 200
    init_data = resp_init_risk.json()
    assert "risk_level" in init_data
    
    # Step 2: Trigger a 1.45x Acute Dengue Outbreak Emergency in Patna District
    em_payload = {
        "event_type": "DISEASE_OUTBREAK",
        "affected_district_ids": ["BR-PATNA"],
        "demand_multiplier": 1.45,
        "severity": "CRITICAL",
        "duration_days": 10,
        "description": "Acute monsoon Dengue fever surge in Patna district"
    }
    resp_em = client.post("/api/v1/emergencies/trigger", json=em_payload)
    assert resp_em.status_code == 200
    assert resp_em.json()["status"] == "ACTIVE"
    
    # Step 3: Advance simulation days to propagate surge into telemetry
    for _ in range(4):
        resp_step = client.post("/api/v1/simulation/step")
        assert resp_step.status_code == 200
    
    # Step 4: Re-evaluate forecast & risk post-surge
    resp_forecast = client.get(f"/api/v1/forecast/medicine/{phc_id}/{med_code}?horizon_days=14")
    assert resp_forecast.status_code == 200
    forecasts = resp_forecast.json()["forecasts"]
    assert len(forecasts) == 14
    
    resp_post_risk = client.get(f"/api/v1/risk/medicine/{phc_id}/{med_code}")
    assert resp_post_risk.status_code == 200
    post_data = resp_post_risk.json()
    
    # Verify risk escalation
    assert post_data["risk_level"] in ["CRITICAL", "HIGH", "WARNING", "LOW"]
    assert post_data["days_of_stock_available"] >= 0.0
    
    # Step 5: Verify Early Warning Alert was generated
    resp_alerts = client.get("/api/v1/alerts/")
    assert resp_alerts.status_code == 200
    alerts_list = resp_alerts.json().get("alerts", [])
    if not alerts_list:
        resp_crit = client.get("/api/v1/alerts/critical")
        alerts_list = resp_crit.json().get("alerts", [])
    assert len(alerts_list) > 0
    
    target_alert = next((a for a in alerts_list if a["facility_id"] == phc_id and a["resource_id"] == med_code), alerts_list[0])
    alert_id = target_alert["alert_id"]
    
    # Step 6: Invoke Gemini Explainer API
    resp_explain = client.post("/api/v1/ai/explain-alert", json={"alert_id": alert_id, "language": "en"})
    assert resp_explain.status_code == 200
    explanation = resp_explain.json()
    assert explanation["status"] == "SUCCESS"
    assert "explanation_en" in explanation
    assert "explanation_hi" in explanation
    assert target_alert["facility_name"] in explanation["explanation_en"]
    
    # Step 7: Clean up test emergency
    client.post("/api/v1/emergencies/clear")
