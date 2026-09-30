"""
Swasthya Records - Gemini Grounded Explainer API Endpoints
"""

from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
from backend.app.services.gemini_explainer import gemini_explainer

router = APIRouter()

class ExplainAlertRequest(BaseModel):
    alert_id: str = Field(description="ID of the early warning alert to explain")
    language: Optional[str] = Field(default="en", description="Language: 'en' for English, 'hi' for Hindi")

from backend.app.services.gemini_redistribution_explainer import gemini_redistribution_explainer

class ExplainRedistributionRequest(BaseModel):
    recommendation_id: Optional[str] = Field(None, description="Optional recommendation ID")
    recommendation_payload: Optional[dict] = Field(None, description="Full recommendation payload")
    language: Optional[str] = Field(default="en", description="Language: 'en' for English, 'hi' for Hindi")

@router.post("/explain-alert", summary="Generate a grounded natural-language explanation for an early warning alert using Gemini")
def explain_alert(req: ExplainAlertRequest):
    result = gemini_explainer.explain_alert(req.alert_id, language=req.language or "en")
    if result.get("status") == "ERROR":
        raise HTTPException(status_code=404, detail=result.get("explanation_en"))
    return result

@router.post("/explain-redistribution", summary="Generate a grounded explanation for a redistribution recommendation")
def explain_redistribution(req: ExplainRedistributionRequest):
    payload = req.recommendation_payload
    if not payload and req.recommendation_id:
        from backend.app.services.simulation_manager import simulation_manager
        payload = simulation_manager.cached_recommendations.get(req.recommendation_id)
        
    if not payload:
        return {
            "status": "INSUFFICIENT_EVIDENCE",
            "explanation_en": "There is insufficient evidence to determine this reliably.",
            "explanation_hi": "विश्वसनीय रूप से यह निर्धारित करने के लिए पर्याप्त डेटा उपलब्ध नहीं है।"
        }
        
    return gemini_redistribution_explainer.explain_recommendation(payload, language=req.language or "en")
