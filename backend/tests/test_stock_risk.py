"""
Unit Tests for Stock-Out Risk Engine & DOSA Calculations
"""

import pytest
from backend.app.services.risk_engine import risk_engine

def test_stock_risk_evaluation():
    risk_data = risk_engine.evaluate_medicine_stock_risk("PHC-BR-PAT-001", "MED-PCM-500")
    
    assert "risk_level" in risk_data
    assert risk_data["risk_level"] in ["CRITICAL", "HIGH", "WARNING", "LOW"]
    assert "days_of_stock_available" in risk_data
    assert risk_data["days_of_stock_available"] >= 0
    assert "safety_stock_threshold" in risk_data
    assert "evidence_summary" in risk_data
    assert len(risk_data["projected_trajectory"]) == 14

def test_risk_level_heuristics():
    all_risks = risk_engine.evaluate_all_facility_risks()
    assert len(all_risks) > 0
    
    for r in all_risks:
        dosa = r["days_of_stock_available"]
        risk = r["risk_level"]
        
        # Verify classification rules
        if dosa < 2.0 or r["current_stock"] == 0:
            assert risk == "CRITICAL"
        elif dosa < 5.0:
            assert risk in ["CRITICAL", "HIGH"]
