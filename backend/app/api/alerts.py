"""
Swasthya Records - Early Warning Alerts API Endpoints
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from backend.app.services.alert_engine import alert_engine

router = APIRouter()

@router.get("", summary="List all active early warning alerts")
@router.get("/", include_in_schema=False)
def list_alerts(
    min_severity: str = Query(default="WARNING", description="INFO, WARNING, HIGH, CRITICAL"),
    alert_type: Optional[str] = Query(None, description="Filter by type: MEDICINE_STOCKOUT_RISK, BED_CAPACITY_RISK, STAFF_SHORTAGE_RISK"),
    facility_id: Optional[str] = Query(None, description="Filter by facility ID")
):
    alerts = alert_engine.generate_all_active_alerts(min_severity=min_severity)
    if alert_type:
        alerts = [a for a in alerts if a["alert_type"] == alert_type]
    if facility_id:
        alerts = [a for a in alerts if a["facility_id"] == facility_id]
    return {
        "total_active_alerts": len(alerts),
        "alerts": alerts
    }

@router.get("/critical", summary="List only CRITICAL priority early warnings")
def get_critical_alerts():
    alerts = alert_engine.generate_all_active_alerts(min_severity="CRITICAL")
    return {
        "total_critical_alerts": len(alerts),
        "alerts": alerts
    }

@router.get("/{alert_id}", summary="Get specific early warning alert details by ID")
def get_alert_details(alert_id: str):
    alert = alert_engine.get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found.")
    return alert
