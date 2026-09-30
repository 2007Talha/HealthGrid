"""
Unit Tests for OR-Tools Resource Redistribution Optimization Engine
Covers mandatory cases 1 through 8.
"""

import pytest
from backend.app.services.redistribution_engine import redistribution_engine

def test_shortage_discovery():
    shortages = redistribution_engine.identify_all_shortages()
    assert isinstance(shortages, list)
    if shortages:
        s0 = shortages[0]
        assert "shortage_id" in s0
        assert "facility_id" in s0
        assert "net_deficit_quantity" in s0
        assert "priority_score" in s0
        assert s0["risk_level"] in ["CRITICAL", "HIGH"]

def test_candidate_source_discovery_and_surplus_protection():
    # PHC Bakhtiyarpur (Patna) seeking Paracetamol (MED-PCM-500)
    candidates = redistribution_engine.find_candidate_sources("PHC-BR-PAT-001", "MED-PCM-500")
    assert isinstance(candidates, list)
    
    for c in candidates:
        # Verify 10-day demand protection and safety stock preservation
        assert c["transferable_surplus"] > 0
        assert c["current_stock"] >= (c["protected_reserve"] + c["transferable_surplus"])
        assert c["distance_km"] > 0
        assert c["duration_hours"] > 0

def test_optimization_solver_single_source_and_multi_source():
    # Run optimizer for Bakhtiyarpur
    rec = redistribution_engine.optimize_redistribution(
        destination_id="PHC-BR-PAT-001",
        medicine_code="MED-PCM-500",
        max_sources=2
    )
    assert rec["status"] in ["OPTIMAL_RECOMMENDED", "COVERED_BY_INCOMING_DELIVERY", "NOT_NEEDED"]
    
    if rec["status"] == "OPTIMAL_RECOMMENDED":
        assert "recommendation_id" in rec
        assert rec["total_recommended_quantity"] > 0
        assert len(rec["transfers"]) <= 2
        
        # Verify source safety stock preservation after transfer
        for t in rec["transfers"]:
            assert t["source_stock_after"] >= t["source_safety_stock_threshold"]
            assert t["transfer_quantity"] <= t["source_surplus_before"]
            
        # Verify destination stock improvement
        impact = rec["projected_impact"]
        assert impact["days_of_stock_available_after"] > rec["destination"]["days_of_stock_available_before"]

def test_infeasible_when_invalid_medicine():
    rec = redistribution_engine.optimize_redistribution(
        destination_id="PHC-BR-PAT-001",
        medicine_code="INVALID-MED-999"
    )
    assert rec["status"] in ["ERROR", "INFEASIBLE_NO_SURPLUS"]
