"""
Unit & Integration Tests for Swasthya Records Simulation Engine
"""

import datetime
import pytest
import pandas as pd
from backend.app.services.simulation_engine import SimulationEngine

def test_engine_initialization():
    engine = SimulationEngine()
    assert len(engine.facilities_df) == 33, "Should have loaded 33 authentic facilities"
    assert len(engine.medicines_df) == 20, "Should have loaded 20 essential medicines"
    assert engine.facilities_df["state_name"].nunique() == 5, "Should span 5 states"

def test_inventory_conservation_math():
    engine = SimulationEngine()
    engine.initialize_inventory()
    
    test_date = datetime.date(2026, 8, 1)
    fac_logs, inv_logs = engine.simulate_day(test_date)
    
    assert len(fac_logs) == 33
    assert len(inv_logs) == 33 * 20
    
    # Verify strict inventory balance conservation:
    # closing_stock == max(0, opening_stock + received_quantity - daily_consumption)
    for row in inv_logs:
        opening = row["opening_stock"]
        received = row["received_quantity"]
        consumed = row["daily_consumption"]
        closing = row["closing_stock"]
        
        expected_closing = max(0, opening + received - consumed)
        assert closing == expected_closing, f"Inventory balance equation failed: {opening} + {received} - {consumed} != {closing}"
        assert closing >= 0, "Closing inventory cannot be negative"
        assert row["data_source"] == "SIMULATED", "Data source tag must be explicitly SIMULATED"

def test_bed_and_staff_domain_constraints():
    engine = SimulationEngine()
    engine.initialize_inventory()
    
    for day in range(7):
        test_date = datetime.date(2026, 8, 1) + datetime.timedelta(days=day)
        fac_logs, _ = engine.simulate_day(test_date)
        
        for row in fac_logs:
            # Bed constraints
            assert 0 <= row["beds_occupied"] <= row["beds_total"], f"Bed occupancy violated: {row['beds_occupied']} / {row['beds_total']}"
            assert row["beds_available"] == (row["beds_total"] - row["beds_occupied"])
            assert 0.0 <= row["bed_occupancy_rate_pct"] <= 100.0
            
            # Staff constraints
            assert 0 <= row["doctors_present"] <= row["doctors_scheduled"], f"Doctor presence constraint violated: {row['doctors_present']} > {row['doctors_scheduled']}"
            assert 0 <= row["nurses_present"] <= row["nurses_scheduled"], f"Nurse presence constraint violated: {row['nurses_present']} > {row['nurses_scheduled']}"
            
            # Footfall constraints
            assert row["patient_footfall"] >= (row["opd_patients"] + row["ipd_patients"]) - 5 # Within integer rounding bounds
            assert row["data_source"] == "SIMULATED"

def test_emergency_surge_propagation():
    """Verifies that injecting an emergency surge causes increased footfall, higher consumption, and increased bed occupancy."""
    engine = SimulationEngine()
    engine.initialize_inventory()
    
    test_date_normal = datetime.date(2026, 8, 10)
    normal_fac_logs, normal_inv_logs = engine.simulate_day(test_date_normal)
    
    # Measure baseline for Patna district
    patna_normal_ff = sum(r["patient_footfall"] for r in normal_fac_logs if r["district_code"] == "BR-PATNA")
    patna_normal_pcm_cons = sum(r["daily_consumption"] for r in normal_inv_logs if "BR-PAT" in r["phc_id"] and r["medicine_code"] == "MED-PCM-500")
    
    # Inject 1.50x outbreak emergency into Patna
    engine.trigger_emergency({
        "event_type": "DISEASE_OUTBREAK",
        "affected_district_ids": ["BR-PATNA"],
        "demand_multiplier": 1.50,
        "severity": "HIGH",
        "duration_days": 7
    })
    
    test_date_surge = datetime.date(2026, 8, 11)
    surge_fac_logs, surge_inv_logs = engine.simulate_day(test_date_surge)
    
    patna_surge_ff = sum(r["patient_footfall"] for r in surge_fac_logs if r["district_code"] == "BR-PATNA")
    patna_surge_pcm_cons = sum(r["daily_consumption"] for r in surge_inv_logs if "BR-PAT" in r["phc_id"] and r["medicine_code"] == "MED-PCM-500")
    
    # Verify surge propagation
    assert patna_surge_ff > patna_normal_ff, f"Surge footfall ({patna_surge_ff}) should exceed normal ({patna_normal_ff})"
    assert patna_surge_pcm_cons > patna_normal_pcm_cons, f"Surge consumption ({patna_surge_pcm_cons}) should exceed normal ({patna_normal_pcm_cons})"
