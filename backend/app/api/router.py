"""
Swasthya Records - API Master Router
"""

from fastapi import APIRouter
from backend.app.api.facilities import router as facilities_router
from backend.app.api.operational import router as operational_router
from backend.app.api.simulation import router as simulation_router
from backend.app.api.emergencies import router as emergencies_router
from backend.app.api.forecasting import router as forecasting_router
from backend.app.api.risk import router as risk_router
from backend.app.api.alerts import router as alerts_router
from backend.app.api.ai import router as ai_router
from backend.app.api.redistribution import router as redistribution_router
from backend.app.api.copilot import router as copilot_router

api_router = APIRouter()

api_router.include_router(facilities_router, prefix="/facilities", tags=["Facilities"])
api_router.include_router(operational_router, prefix="/operational", tags=["Operational Telemetry"])
api_router.include_router(simulation_router, prefix="/simulation", tags=["Simulation Engine"])
api_router.include_router(emergencies_router, prefix="/emergencies", tags=["Emergencies"])
api_router.include_router(forecasting_router, prefix="/forecast", tags=["AI Forecasting"])
api_router.include_router(risk_router, prefix="/risk", tags=["Stock-Out Risk"])
api_router.include_router(alerts_router, prefix="/alerts", tags=["Early Warnings"])
api_router.include_router(ai_router, prefix="/ai", tags=["Gemini Explainer"])
api_router.include_router(redistribution_router, tags=["Resource Redistribution"])
api_router.include_router(copilot_router, prefix="/copilot", tags=["Operations Copilot"])
