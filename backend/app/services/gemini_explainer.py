"""
Swasthya Records - Gemini Operations Explainer & Grounded Reasoning Service
Provides natural-language and multilingual (English & Hindi) explanations of critical early warnings and forecasts.
Strictly grounded on verified database evidence without hallucinations or clinical medical advice.
"""

import os
import json
import logging
import requests

from backend.app.services.alert_engine import alert_engine

logger = logging.getLogger("swasthya.gemini")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

STRICT_SYSTEM_PROMPT = """You are the Swasthya Records Operations Copilot, an AI assistant for Indian public health supply-chain and resource management.
Rules:
1. You MUST retrieve all factual numbers, stock levels, bed counts, footfalls, and optimization numbers directly from the verified Evidence Payload.
2. NEVER invent or extrapolate numbers. If the payload is empty or insufficient, reply:
   "There is insufficient evidence to determine this reliably."
3. You are a LOGISTICS AND RESOURCE MANAGEMENT SYSTEM. You MUST NOT diagnose illnesses, prescribe medications, or give individual clinical treatment advice.
4. Keep answers concise, factual, and actionable for district healthcare officers.
5. Provide the explanation in the requested language (English and Hindi)."""


class GeminiExplainer:
    def explain_alert(self, alert_id, language="en"):
        """Generates a structured, evidence-grounded explanation for an early warning alert."""
        alert = alert_engine.get_alert_by_id(alert_id)
        if not alert:
            return {
                "alert_id": alert_id,
                "status": "ERROR",
                "explanation_en": "There is insufficient evidence to determine this reliably.",
                "explanation_hi": "इसकी पुष्टि करने के लिए पर्याप्त डेटा उपलब्ध नहीं है।",
                "evidence_grounding": None,
            }

        # Grounded structured payload
        payload_context = {
            "alert_id": alert["alert_id"],
            "severity": alert["severity"],
            "alert_type": alert["alert_type"],
            "facility_name": alert["facility_name"],
            "resource_name": alert["resource_name"],
            "evidence_summary": alert["evidence_summary"],
            "projected_impact": alert["projected_impact"],
            "recommended_next_step": alert["recommended_next_step"],
        }

        # If API key available, invoke Gemini 1.5 Flash via REST
        if GEMINI_API_KEY:
            try:
                prompt_text = (
                    f"System Policy:\n{STRICT_SYSTEM_PROMPT}\n\n"
                    f"Evidence Payload:\n{json.dumps(payload_context, indent=2)}\n\n"
                    f"Task: Explain why this alert was generated, cite the exact numbers from the evidence payload, and summarize the recommended operational next step. Provide both English and Hindi versions."
                )

                req_body = {
                    "contents": [{"parts": [{"text": prompt_text}]}],
                    "generationConfig": {"temperature": 0.1, "maxOutputTokens": 500},
                }

                resp = requests.post(GEMINI_ENDPOINT, json=req_body, timeout=8)
                if resp.status_code == 200:
                    resp_json = resp.json()
                    gen_text = resp_json["candidates"][0]["content"]["parts"][0]["text"]
                    return {
                        "alert_id": alert_id,
                        "status": "SUCCESS",
                        "model_used": "Gemini 1.5 Flash (GCP Grounded)",
                        "explanation_en": gen_text,
                        "evidence_grounding": payload_context,
                    }
            except Exception as e:
                logger.warning(
                    "Gemini API call failed, using deterministic grounded synthesizer: %s",
                    e,
                )

        # Deterministic Grounded Reasoning Engine Fallback (Guaranteed 100% factual, zero-hallucination)
        fac = alert["facility_name"]
        res = alert["resource_name"]
        sev = alert["severity"]
        ev = alert["evidence_summary"]
        impact = alert["projected_impact"]
        rec = alert["recommended_next_step"]

        explanation_en = (
            f"**Operational Alert Summary ({sev} Priority)**\n\n"
            f"• **Facility Affected**: {fac}\n"
            f"• **Resource Under Pressure**: {res}\n"
            f"• **Root Cause & Evidence**: {ev}\n"
            f"• **Projected Operational Impact**: {impact}\n"
            f"• **Recommended Action**: {rec}\n\n"
            f"*(Note: Derived strictly from verified telemetry and numerical ML demand forecasts.)*"
        )

        explanation_hi = (
            f"**परिचालन चेतावनी सारांश ({sev} प्राथमिकता)**\n\n"
            f"• **प्रभावित स्वास्थ्य केंद्र**: {fac}\n"
            f"• **संसाधन**: {res}\n"
            f"• **साक्ष्य एवं कारण**: {ev}\n"
            f"• **अनुमानित प्रभाव**: {impact}\n"
            f"• **अनुशंसित कार्रवाई**: {rec}\n\n"
            f"*(यह विश्लेषण वास्तविक डेटा और सांख्यिकीय मांग पूर्वानुमान पर आधारित है।)*"
        )

        return {
            "alert_id": alert_id,
            "status": "SUCCESS",
            "model_used": "Swasthya Grounded Explainer Engine",
            "explanation_en": explanation_en,
            "explanation_hi": explanation_hi,
            "evidence_grounding": payload_context,
        }


gemini_explainer = GeminiExplainer()
