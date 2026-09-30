"""
Unit Tests for Early Warning Alert Engine & Gemini Grounded Explainer
"""

import pytest
from backend.app.services.alert_engine import alert_engine
from backend.app.services.gemini_explainer import gemini_explainer

def test_alert_generation():
    alerts = alert_engine.generate_all_active_alerts(min_severity="WARNING")
    assert isinstance(alerts, list)
    
    for alert in alerts:
        assert "alert_id" in alert
        assert "severity" in alert
        assert alert["severity"] in ["CRITICAL", "HIGH", "WARNING", "INFO"]
        assert "alert_type" in alert
        assert "evidence_summary" in alert
        assert "projected_impact" in alert
        assert "recommended_next_step" in alert

def test_gemini_grounded_explanation():
    alerts = alert_engine.generate_all_active_alerts(min_severity="HIGH")
    if alerts:
        target_alert = alerts[0]
        alert_id = target_alert["alert_id"]
        
        explanation = gemini_explainer.explain_alert(alert_id)
        assert explanation["status"] == "SUCCESS"
        assert "explanation_en" in explanation
        assert "explanation_hi" in explanation
        assert target_alert["facility_name"] in explanation["explanation_en"]
        assert explanation["evidence_grounding"] is not None

def test_gemini_guardrail_insufficient_evidence():
    fake_alert_id = "ALT-NON-EXISTENT-999"
    res = gemini_explainer.explain_alert(fake_alert_id)
    assert res["status"] == "ERROR"
    assert "There is insufficient evidence to determine this reliably." in res["explanation_en"]
