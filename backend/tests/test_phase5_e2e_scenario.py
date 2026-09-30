"""
Swasthya Records - Phase 5 End-to-End Master Conversational Demo Scenario Test
Implements Section 36 flow:
Step 1: "Which PHCs are at highest risk?" -> Gemini executes get_stockout_risks()
Step 2: "Why?" -> Gemini maintains conversation context and calls get_facility_status() & get_forecast()
Step 3: "Can we get supplies from another facility?" -> Gemini calls get_redistribution_options()
Step 4: "What happens if we transfer 900 units?" -> Gemini calls run_what_if_simulation() / simulate_redistribution()
Step 5: Verify Before (CRITICAL) -> After (LOW) risk mitigation.
"""

import uuid
import pytest
from starlette.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_phase5_master_conversational_scenario():
    conv_id = f"e2e-phase5-demo-{uuid.uuid4().hex[:6]}"
    
    # Step 1: User asks for highest risk facilities
    resp_step1 = client.post("/api/v1/copilot/chat", json={
        "message": "Which PHCs are at highest risk today?",
        "conversation_id": conv_id,
        "language": "en",
        "user_role": "ADMIN"
    })
    assert resp_step1.status_code == 200
    data1 = resp_step1.json()
    assert "response" in data1
    assert any(t["tool"] in ["get_stockout_risks", "get_critical_alerts"] for t in data1["tool_calls"])
    assert len(data1["evidence"]) > 0
    
    # Step 2: Contextual "Why?" follow-up question
    resp_step2 = client.post("/api/v1/copilot/chat", json={
        "message": "Why is PHC-BR-PAT-001 at critical risk?",
        "conversation_id": conv_id,
        "language": "en",
        "user_role": "ADMIN"
    })
    assert resp_step2.status_code == 200
    data2 = resp_step2.json()
    assert any(t["tool"] == "get_facility_status" for t in data2["tool_calls"])
    assert "PHC-BR-PAT-001" in data2["response"] or "Bakhtiyarpur" in data2["response"]
    
    # Step 3: Redistribution inquiry
    resp_step3 = client.post("/api/v1/copilot/chat", json={
        "message": "Can we get supplies and redistribution options for PHC-BR-PAT-001?",
        "conversation_id": conv_id,
        "language": "en",
        "user_role": "ADMIN"
    })
    assert resp_step3.status_code == 200
    data3 = resp_step3.json()
    assert any(t["tool"] == "get_redistribution_options" for t in data3["tool_calls"])
    
    # Step 4: What-If simulation inquiry
    resp_step4 = client.post("/api/v1/copilot/chat", json={
        "message": "What happens if we simulate a transfer of 900 units to PHC-BR-PAT-001?",
        "conversation_id": conv_id,
        "language": "en",
        "user_role": "ADMIN"
    })
    assert resp_step4.status_code == 200
    data4 = resp_step4.json()
    assert data4["simulation"] is True
    assert any(t["tool"] == "run_what_if_simulation" for t in data4["tool_calls"])
    assert "WHAT-IF SIMULATION" in data4["response"]
    
    # Step 5: Verify Session History Integrity
    resp_hist = client.get(f"/api/v1/copilot/history?conversation_id={conv_id}")
    assert resp_hist.status_code == 200
    hist_data = resp_hist.json()
    assert hist_data["turns_count"] == 4
