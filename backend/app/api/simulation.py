"""
Swasthya Records - Simulation Engine Controls API
"""

from typing import Optional
import datetime
from fastapi import APIRouter, HTTPException, Query
from backend.app.schemas.simulation import EmergencyScenarioRequest, EmergencyScenarioResponse, SimulationRunStatus
from backend.app.services.simulation_engine import simulation_engine

router = APIRouter()

@router.post("/generate-history", summary="Generate N days of synthetic historical operational time-series")
def generate_history(days: int = Query(default=90, ge=7, le=365)):
    result = simulation_engine.generate_historical_timeseries(days=days)
    return {
        "status": "SUCCESS",
        "message": f"Generated {days} days of realistic operational time-series",
        "details": result
    }

@router.post("/step", summary="Advance the simulation forward by 1 day")
def step_simulation():
    next_date = simulation_engine.current_sim_date + datetime.timedelta(days=1)
    simulation_engine.current_sim_date = next_date
    fac_logs, inv_logs = simulation_engine.simulate_day(next_date)
    simulation_engine.facility_daily_logs.extend(fac_logs)
    simulation_engine.inventory_daily_logs.extend(inv_logs)
    simulation_engine.export_processed_data()
    from backend.app.services.risk_engine import risk_engine
    risk_engine.clear_cache()
    return {
        "status": "SUCCESS",
        "advanced_to_date": next_date.isoformat(),
        "facilities_simulated": len(fac_logs),
        "inventory_records_simulated": len(inv_logs)
    }

@router.get("/status", response_model=SimulationRunStatus, summary="Get current simulator state and active scenarios")
def get_simulation_status():
    emergencies = [
        EmergencyScenarioResponse(
            scenario_id=s["scenario_id"],
            event_type=s["event_type"],
            affected_district_ids=s["affected_district_ids"],
            demand_multiplier=s["demand_multiplier"],
            severity=s["severity"],
            duration_days=s.get("duration_days", 7),
            facilities_impacted_count=s.get("facilities_impacted_count", 0),
            status=s.get("status", "ACTIVE"),
            created_at=datetime.datetime.now(datetime.timezone.utc)
        )
        for s in simulation_engine.active_emergencies.values()
    ]
    return SimulationRunStatus(
        is_running=True,
        current_simulated_date=simulation_engine.current_sim_date,
        historical_days_generated=len(simulation_engine.facility_daily_logs) // max(1, len(simulation_engine.facilities_df)),
        total_facilities_tracked=len(simulation_engine.facilities_df),
        total_medicines_tracked=len(simulation_engine.medicines_df),
        total_inventory_records=len(simulation_engine.inventory_daily_logs),
        active_emergency_scenarios=emergencies,
        last_updated_at=datetime.datetime.now(datetime.timezone.utc)
    )

@router.post("/reset", summary="Reset simulation inventory to default baseline")
def reset_simulation():
    simulation_engine.initialize_inventory()
    simulation_engine.active_emergencies.clear()
    from backend.app.services.simulation_manager import simulation_manager
    from backend.app.services.risk_engine import risk_engine
    simulation_manager.reset_all_simulations()
    risk_engine.clear_cache()
    return {
        "status": "SUCCESS",
        "message": "Simulation inventory, emergencies, and redistribution transfers successfully reset to baseline."
    }

@router.post("/demo-seed", summary="Inject deterministic judge demo scenario")
def seed_demo_scenario():
    """
    Deterministic demo scenario:
    1. Resets system to clean baseline.
    2. Injects high-demand flood surge in target demo region (Patna District, Bihar).
    3. Multiplies demand for critical rehydration and antipyretic supplies (ORS, PCM).
    4. Returns scenario coordinates and expected risk progression.
    """
    # 1. Deterministic baseline reset
    simulation_engine.initialize_inventory()
    simulation_engine.active_emergencies.clear()
    from backend.app.services.simulation_manager import simulation_manager
    from backend.app.services.risk_engine import risk_engine
    simulation_manager.reset_all_simulations()
    risk_engine.clear_cache()

    # 2. Inject flood surge
    scenario = simulation_engine.trigger_emergency({
        "event_type": "FLOOD",
        "affected_district_ids": ["BR-PATNA"],
        "demand_multiplier": 3.2,
        "severity": "CRITICAL",
        "duration_days": 10
    })

    return {
        "status": "SUCCESS",
        "scenario": "DEMO_DETERMINISTIC_SURGE",
        "affected_region": "Patna District, Bihar (IN-BR)",
        "resource": "MED-ORS-POW (Oral Rehydration Salts)",
        "destination_facility": "PHC-BR-PAT-001",
        "candidate_source": "PHC-BR-PAT-002",
        "expected_before_risk": "CRITICAL",
        "expected_after_risk": "LOW",
        "scenario_details": scenario
    }

