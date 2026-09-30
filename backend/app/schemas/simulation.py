"""
Swasthya Records - Simulation Engine Schemas
"""

from typing import Optional, List, Dict
from datetime import date, datetime
from pydantic import BaseModel, Field

class EmergencyScenarioRequest(BaseModel):
    event_type: str = Field(description="PATIENT_SURGE, FLOOD, HEATWAVE, DISEASE_OUTBREAK, SUPPLY_DISRUPTION")
    affected_district_ids: List[str] = Field(description="Target District Codes, e.g. ['BR-PATNA', 'UP-VARANASI']")
    demand_multiplier: float = Field(default=1.40, ge=1.0, le=5.0, description="Demand acceleration factor")
    severity: str = Field(default="HIGH", description="LOW, MEDIUM, HIGH, CRITICAL")
    duration_days: int = Field(default=7, ge=1, le=30)
    description: Optional[str] = "Simulated acute surge scenario"

class EmergencyScenarioResponse(BaseModel):
    scenario_id: str
    event_type: str
    affected_district_ids: List[str]
    demand_multiplier: float
    severity: str
    duration_days: int
    facilities_impacted_count: int
    status: str = "ACTIVE"
    created_at: datetime

class SimulationRunStatus(BaseModel):
    is_running: bool = False
    current_simulated_date: date
    historical_days_generated: int
    total_facilities_tracked: int
    total_medicines_tracked: int
    total_inventory_records: int
    active_emergency_scenarios: List[EmergencyScenarioResponse] = []
    last_updated_at: datetime
