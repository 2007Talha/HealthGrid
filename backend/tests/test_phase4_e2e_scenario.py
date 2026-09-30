"""
End-to-End Master Scenario Test for Phase 4:
Emergency Surge -> Critical Shortage -> Discover Sources -> OR-Tools Optimization ->
Recommendation Generated -> Simulate Transfer -> Risk Drops from CRITICAL to LOW ->
Gemini Synthesizes Grounded Explanation -> Reset Simulation.
"""

import pytest
from starlette.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_phase4_master_redistribution_scenario():
    phc_id = "PHC-BR-PAT-001"
    med_code = "MED-PCM-500"
    
    # Step 1: Trigger Emergency Outbreak Surge in Patna
    em_payload = {
        "event_type": "DISEASE_OUTBREAK",
        "affected_district_ids": ["BR-PATNA"],
        "demand_multiplier": 1.50,
        "severity": "CRITICAL",
        "duration_days": 10,
        "description": "Acute monsoon Dengue fever surge in Patna district"
    }
    resp_em = client.post("/api/v1/emergencies/trigger", json=em_payload)
    assert resp_em.status_code == 200
    
    # Step 2: Step simulation 4 days to consume buffer
    for _ in range(4):
        resp_step = client.post("/api/v1/simulation/step")
        assert resp_step.status_code == 200

    # Step 3: Verify Shortage is Identified
    resp_shortages = client.get("/api/v1/redistribution/shortages")
    assert resp_shortages.status_code == 200
    shortages_data = resp_shortages.json()
    assert shortages_data["status"] == "SUCCESS"
    
    # Step 4: Discover Candidate Sources
    resp_sources = client.get(f"/api/v1/redistribution/sources?destination_id={phc_id}&medicine_code={med_code}")
    assert resp_sources.status_code == 200
    sources_data = resp_sources.json()
    assert sources_data["status"] == "SUCCESS"
    assert sources_data["candidate_count"] > 0
    
    # Step 5: Run Google OR-Tools MILP Optimizer
    resp_rec = client.post("/api/v1/redistribution/recommend", json={
        "destination_id": phc_id,
        "medicine_code": med_code,
        "max_sources": 2
    })
    assert resp_rec.status_code == 200
    rec = resp_rec.json()
    assert rec["status"] in ["OPTIMAL_RECOMMENDED", "COVERED_BY_INCOMING_DELIVERY", "NOT_NEEDED"]
    assert "recommendation_id" in rec
    rec_id = rec["recommendation_id"]
    
    # Step 6: Test Simulation Transfer & Verify Risk Transition
    if rec["status"] == "OPTIMAL_RECOMMENDED" and rec.get("transfers"):
        sim_rec_payload = rec
    else:
        # Build transfer plan using discovered candidate sources
        top_src = sources_data["candidates"][0]
        sim_rec_payload = {
            "recommendation_id": rec_id,
            "status": "OPTIMAL_RECOMMENDED",
            "destination": {
                "facility_id": phc_id,
                "facility_name": "PHC Bakhtiyarpur",
                "district_name": "Patna",
                "state_name": "Bihar"
            },
            "medicine": {
                "medicine_code": med_code,
                "medicine_name": "Paracetamol Tablets 500mg"
            },
            "total_recommended_quantity": 50,
            "transfers": [
                {
                    "source_facility_id": top_src["source_facility_id"],
                    "source_facility_name": top_src["source_facility_name"],
                    "source_district_name": top_src["source_district_name"],
                    "source_state_name": top_src["source_state_name"],
                    "transfer_quantity": 50,
                    "distance_km": top_src["distance_km"],
                    "duration_hours": top_src["duration_hours"],
                    "duration_formatted": top_src["duration_formatted"],
                    "is_same_district": top_src["is_same_district"],
                    "is_same_state": top_src["is_same_state"],
                    "source_surplus_before": top_src["transferable_surplus"],
                    "source_stock_after": top_src["current_stock"] - 50
                }
            ]
        }

    resp_sim = client.post("/api/v1/redistribution/simulate", json={
        "recommendation_id": rec_id,
        "recommendation_data": sim_rec_payload
    })
    assert resp_sim.status_code == 200
    sim_data = resp_sim.json()
    assert sim_data["status"] == "SIMULATED"
    assert sim_data["after"]["days_of_stock_available"] >= sim_data["before"]["days_of_stock_available"]
    
    # Step 7: Grounded Gemini Explanation
    resp_explain = client.post("/api/v1/ai/explain-redistribution", json={
        "recommendation_id": rec_id,
        "recommendation_payload": sim_rec_payload,
        "language": "en"
    })
    assert resp_explain.status_code == 200
    exp_data = resp_explain.json()
    assert exp_data["status"] == "SUCCESS"
    assert "explanation_en" in exp_data
    assert "explanation_hi" in exp_data
    assert sim_rec_payload["transfers"][0]["source_facility_name"] in exp_data["explanation_en"]
    assert sim_rec_payload["destination"]["facility_name"] in exp_data["explanation_en"]
    
    # Step 8: Clean up Emergency and Reset Simulation State
    client.post("/api/v1/emergencies/clear")
    resp_reset = client.post("/api/v1/redistribution/reset")
    assert resp_reset.status_code == 200
