"""
Swasthya Records - BRICS Federated Learning API Endpoints
"""

from typing import Dict, Any
from fastapi import APIRouter
from backend.app.services.federated_learning import brics_federated_engine

router = APIRouter(prefix="/federated", tags=["BRICS Federated Learning"])

@router.get("/status")
async def get_federated_status() -> Dict[str, Any]:
    """Returns the real-time status of cross-border BRICS federated learning models."""
    return brics_federated_engine.get_federated_status()

@router.post("/aggregate")
async def trigger_federated_round() -> Dict[str, Any]:
    """Simulates a secure model weight aggregation round across participating BRICS nodes."""
    return brics_federated_engine.simulate_federated_round()
