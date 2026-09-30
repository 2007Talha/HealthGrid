"""
Unit Tests for Reversible Redistribution Simulation State Manager & API Endpoints
"""

import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.services.simulation_manager import simulation_manager
from backend.app.services.redistribution_engine import redistribution_engine

client = TestClient(app)

def test_simulation_workflow_and_risk_reduction():
    dest_id = "PHC-BR-PAT-001"
    med_code = "MED-PCM-500"
    
    # 1. Generate Recommendation
    rec = redistribution_engine.optimize_redistribution(dest_id, med_code)
    if rec.get("status") == "OPTIMAL_RECOMMENDED":
        rec_id = rec["recommendation_id"]
        
        # 2. Execute Simulation
        sim_res = simulation_manager.apply_simulated_transfer(rec_id, rec_data=rec)
        assert sim_res["status"] == "SIMULATED"
        assert "simulation_id" in sim_res
        assert sim_res["after"]["days_of_stock_available"] >= sim_res["before"]["days_of_stock_available"]
        
        # 3. Check SQLite / In-Memory History
        history = simulation_manager.get_simulation_history()
        assert len(history) > 0

def test_simulation_reset():
    reset_res = simulation_manager.reset_all_simulations()
    assert reset_res["status"] == "RESET_SUCCESSFUL"
    assert len(simulation_manager.active_simulations) == 0

def test_redistribution_api_endpoints():
    # Test GET /api/v1/redistribution/shortages
    resp_shortages = client.get("/api/v1/redistribution/shortages")
    assert resp_shortages.status_code == 200
    assert resp_shortages.json()["status"] == "SUCCESS"
    
    # Test GET /api/v1/redistribution/sources
    resp_sources = client.get("/api/v1/redistribution/sources?destination_id=PHC-BR-PAT-001&medicine_code=MED-PCM-500")
    assert resp_sources.status_code == 200
    assert resp_sources.json()["status"] == "SUCCESS"
    
    # Test POST /api/v1/redistribution/recommend
    resp_rec = client.post("/api/v1/redistribution/recommend", json={
        "destination_id": "PHC-BR-PAT-001",
        "medicine_code": "MED-PCM-500",
        "max_sources": 2
    })
    assert resp_rec.status_code == 200
    rec_data = resp_rec.json()
    assert "status" in rec_data
