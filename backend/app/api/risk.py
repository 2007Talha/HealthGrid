"""
Swasthya Records - Stock-Out Risk & Inventory Coverage API Endpoints
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from backend.app.services.risk_engine import risk_engine

router = APIRouter()

@router.get("/medicine/{phc_id}/{medicine_code}", summary="Get detailed stock-out risk assessment and projected exhaustion date")
def get_medicine_stock_risk(phc_id: str, medicine_code: str):
    risk_data = risk_engine.evaluate_medicine_stock_risk(phc_id, medicine_code)
    if risk_data.get("risk_level") == "UNKNOWN":
        raise HTTPException(status_code=404, detail="Insufficient data to evaluate stock risk.")
    return risk_data

@router.get("/facility/{phc_id}", summary="Get stock-out risk assessment across all medicines for a specific facility")
def get_facility_overall_risk(phc_id: str):
    all_risks = risk_engine.evaluate_all_facility_risks()
    fac_risks = [r for r in all_risks if r["phc_id"] == phc_id]
    if not fac_risks:
        raise HTTPException(status_code=404, detail=f"No facility records found for {phc_id}")
    return {
        "phc_id": phc_id,
        "facility_name": fac_risks[0]["facility_name"],
        "total_medicines_evaluated": len(fac_risks),
        "critical_count": sum(1 for r in fac_risks if r["risk_level"] == "CRITICAL"),
        "high_count": sum(1 for r in fac_risks if r["risk_level"] == "HIGH"),
        "warning_count": sum(1 for r in fac_risks if r["risk_level"] == "WARNING"),
        "inventory_risks": fac_risks
    }

@router.get("/critical-hotspots", summary="List all facilities with immediate CRITICAL stock-out risk")
def get_critical_hotspots():
    all_risks = risk_engine.evaluate_all_facility_risks()
    critical_risks = [r for r in all_risks if r["risk_level"] == "CRITICAL"]
    return {
        "total_critical_hotspots": len(critical_risks),
        "critical_hotspots": critical_risks
    }
