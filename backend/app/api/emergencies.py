"""
Swasthya Records - Emergency Management API Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from backend.app.schemas.simulation import EmergencyScenarioRequest, EmergencyScenarioResponse
from backend.app.services.emergency_service import emergency_service

router = APIRouter()

@router.post("/trigger", response_model=EmergencyScenarioResponse, summary="Inject an emergency scenario multiplier into target districts")
def trigger_emergency(scenario: EmergencyScenarioRequest):
    result = emergency_service.trigger_emergency_scenario(scenario.model_dump())
    return EmergencyScenarioResponse(
        scenario_id=result["scenario_id"],
        event_type=result["event_type"],
        affected_district_ids=result["affected_district_ids"],
        demand_multiplier=result["demand_multiplier"],
        severity=result["severity"],
        duration_days=result["duration_days"],
        facilities_impacted_count=result.get("facilities_impacted_count", 0),
        status="ACTIVE",
        created_at=result["created_at"]
    )

@router.get("/active", summary="List all currently active emergency scenarios")
def list_active_emergencies():
    return emergency_service.get_active_emergencies()

@router.post("/clear", summary="Clear an active emergency scenario by ID or clear all")
def clear_emergency(scenario_id: Optional[str] = None):
    return emergency_service.clear_emergency(scenario_id)
