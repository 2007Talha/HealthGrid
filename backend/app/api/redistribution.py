"""
Swasthya Records - Cross-District Resource Redistribution API Endpoints
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query, Depends
from backend.app.services.redistribution_engine import redistribution_engine
from backend.app.services.simulation_manager import simulation_manager
from backend.app.core.rate_limit import rate_limit

router = APIRouter(prefix="/redistribution", tags=["Resource Redistribution"])

class RecommendRequest(BaseModel):
    destination_id: str = Field(..., description="Target facility ID facing resource shortage (e.g. PHC-BR-PAT-001)")
    medicine_code: str = Field(..., description="Target essential medicine code (e.g. MED-PCM-500)")
    max_sources: int = Field(2, description="Maximum number of source facilities to combine")

class SimulateRequest(BaseModel):
    recommendation_id: str = Field(..., description="Unique recommendation ID to approve and simulate")
    recommendation_data: Optional[Dict[str, Any]] = Field(None, description="Optional full recommendation payload")

@router.get("/shortages")
async def get_all_shortages() -> Dict[str, Any]:
    """Retrieves all active facility-medicine shortages eligible for redistribution rebalancing."""
    shortages = redistribution_engine.identify_all_shortages()
    return {
        "status": "SUCCESS",
        "total_shortages": len(shortages),
        "shortages": shortages
    }

@router.get("/sources")
async def get_candidate_sources(
    destination_id: str = Query(..., description="Destination facility ID"),
    medicine_code: str = Query(..., description="Medicine code"),
    max_distance_km: float = Query(300.0, description="Max search radius in km")
) -> Dict[str, Any]:
    """Discovers and ranks nearby source facilities with safe transferable surplus."""
    candidates = redistribution_engine.find_candidate_sources(
        destination_id=destination_id,
        medicine_code=medicine_code,
        max_distance_km=max_distance_km
    )
    return {
        "status": "SUCCESS",
        "destination_id": destination_id,
        "medicine_code": medicine_code,
        "candidate_count": len(candidates),
        "candidates": candidates
    }

@router.post("/recommend", dependencies=[Depends(rate_limit)])
async def generate_redistribution_recommendation(payload: RecommendRequest) -> Dict[str, Any]:
    """Runs Google OR-Tools MILP optimizer to generate an optimal redistribution plan."""
    rec = redistribution_engine.optimize_redistribution(
        destination_id=payload.destination_id,
        medicine_code=payload.medicine_code,
        max_sources=payload.max_sources
    )
    # Cache recommendation for simulation execution
    if rec.get("status") == "OPTIMAL_RECOMMENDED":
        simulation_manager.cache_recommendation(rec)
    return rec

@router.post("/simulate", dependencies=[Depends(rate_limit)])
async def simulate_redistribution_transfer(payload: SimulateRequest) -> Dict[str, Any]:
    """Applies a simulated redistribution transfer and returns Before -> Transfer -> After risk audit."""
    result = simulation_manager.apply_simulated_transfer(
        recommendation_id=payload.recommendation_id,
        rec_data=payload.recommendation_data
    )
    if result.get("status") == "ERROR":
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result

@router.post("/reset")
async def reset_simulations() -> Dict[str, Any]:
    """Clears all simulated redistribution transfers and restores baseline operational telemetry."""
    return simulation_manager.reset_all_simulations()

@router.get("/history")
async def get_simulation_history() -> Dict[str, Any]:
    """Returns audit log of all executed redistribution simulations."""
    history = simulation_manager.get_simulation_history()
    return {
        "status": "SUCCESS",
        "total_simulations": len(history),
        "history": history
    }
