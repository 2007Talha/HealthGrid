"""
Swasthya Records - Gemini Operations Copilot API Endpoints
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query, Header, Depends
from pydantic import BaseModel, Field
from backend.app.services.copilot_service import copilot_service
from backend.app.core.rate_limit import rate_limit

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., description="User prompt or question for SwasthyaGrid Copilot")
    conversation_id: Optional[str] = Field(None, description="Optional conversation context identifier")
    language: str = Field("en", description="Language: 'en' for English, 'hi' for Hindi")
    user_role: str = Field("ADMIN", description="User authorization role: ADMIN, STATE_OPERATOR, DISTRICT_OPERATOR")
    user_id: str = Field("operator-01", description="User identifier for audit logging")

class WhatIfRequest(BaseModel):
    facility_id: str = Field("PHC-BR-PAT-001", description="Target facility ID")
    medicine_code: str = Field("MED-PCM-500", description="Target medicine code")
    demand_surge_pct: float = Field(0.0, description="Percentage surge in daily demand (e.g. 30.0)")
    delivery_delay_days: int = Field(0, description="Simulated shipment delay in days")
    transfer_units: int = Field(0, description="Simulated incoming transfer in units")
    user_role: str = Field("ADMIN", description="User authorization role")

class VoiceRequest(BaseModel):
    audio_base64: str = Field(..., description="Base64-encoded audio payload")
    conversation_id: Optional[str] = Field(None, description="Optional conversation context identifier")
    language: str = Field("en", description="Language: 'en' or 'hi'")
    user_role: str = Field("ADMIN", description="User authorization role")

@router.post("/chat", summary="Interact with SwasthyaGrid Operations Copilot", dependencies=[Depends(rate_limit)])
def chat_with_copilot(req: ChatRequest):
    """
    Submits an operational question to the Copilot. The assistant selects and executes
    deterministic backend tools and returns a grounded response with structured evidence.
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
        
    result = copilot_service.process_query(
        user_message=req.message,
        conversation_id=req.conversation_id,
        user_role=req.user_role,
        user_id=req.user_id,
        language=req.language
    )
    return result

@router.post("/what-if", summary="Run isolated What-If scenario simulation", dependencies=[Depends(rate_limit)])
def run_what_if_simulation(req: WhatIfRequest):
    """
    Simulates hypothetical demand surges, shipment delays, or resource transfers
    in a sandboxed shadow environment without altering baseline production inventory.
    """
    result = copilot_service.run_what_if_simulation(
        facility_id=req.facility_id,
        medicine_code=req.medicine_code,
        demand_surge_pct=req.demand_surge_pct,
        delivery_delay_days=req.delivery_delay_days,
        transfer_units=req.transfer_units
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.post("/voice", summary="Voice-driven query pipeline (Speech-to-Text & Text-to-Speech)", dependencies=[Depends(rate_limit)])
def process_voice_query(req: VoiceRequest):
    """
    Processes audio voice input through Google Cloud Speech-to-Text, executes the Copilot
    tool pipeline, and returns textual and speech synthesis indicators.
    """
    result = copilot_service.process_voice_query(
        audio_base64=req.audio_base64,
        conversation_id=req.conversation_id,
        user_role=req.user_role,
        language=req.language
    )
    return result

@router.get("/history", summary="Retrieve conversation context history")
def get_conversation_history(conversation_id: str = Query(..., description="Conversation ID to retrieve")):
    """
    Returns prior queries and facility context for transparent session audit.
    """
    history = copilot_service.conversations.get(conversation_id, [])
    return {
        "conversation_id": conversation_id,
        "turns_count": len(history),
        "history": history
    }

@router.get("/audit-log", summary="Retrieve tool invocation audit trails")
def get_audit_log(limit: int = Query(50, description="Max log entries to retrieve")):
    """
    Returns immutable audit logs recording tool invocations, parameters, and user roles.
    """
    return {
        "total_entries": len(copilot_service.audit_log),
        "logs": copilot_service.audit_log[-limit:]
    }
