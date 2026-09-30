"""
Swasthya Records - Real-time Operational Telemetry API
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query
from backend.app.services.inventory_service import inventory_service
from backend.app.services.bed_service import bed_service
from backend.app.services.staffing_service import staffing_service
from backend.app.services.delivery_service import delivery_service

router = APIRouter()

@router.get("/inventory/{phc_id}", summary="Get current medicine inventory for a PHC")
def get_phc_inventory(phc_id: str):
    records = inventory_service.get_latest_inventory_by_phc(phc_id)
    if not records:
        raise HTTPException(status_code=404, detail=f"No operational inventory found for {phc_id}")
    return {
        "phc_id": phc_id,
        "total_medicines_tracked": len(records),
        "data_source": "SIMULATED",
        "inventory": records
    }

@router.get("/inventory/history/{phc_id}/{medicine_code}", summary="Get historical inventory time-series for a medicine")
def get_medicine_history(phc_id: str, medicine_code: str):
    history = inventory_service.get_medicine_history(phc_id, medicine_code)
    if not history:
        raise HTTPException(status_code=404, detail=f"No history found for {phc_id} - {medicine_code}")
    return {
        "phc_id": phc_id,
        "medicine_code": medicine_code,
        "data_source": "SIMULATED",
        "time_series_points": len(history),
        "history": history
    }

@router.get("/beds", summary="Get bed availability and occupancy rates")
def get_bed_status(phc_id: Optional[str] = None):
    status = bed_service.get_latest_bed_status(phc_id)
    return {
        "total_facilities": len(status),
        "data_source": "SIMULATED",
        "bed_status": status
    }

@router.get("/beds/history", summary="Get multi-day aggregate bed occupancy history")
def get_bed_history(phc_id: Optional[str] = None, days: int = 14):
    history = bed_service.get_bed_history(phc_id, days=days)
    return {
        "total_days": len(history),
        "data_source": "SIMULATED",
        "bed_history": history
    }

@router.get("/staffing", summary="Get medical staff attendance and shortage flags")
def get_staffing_status(phc_id: Optional[str] = None):
    status = staffing_service.get_latest_staffing_status(phc_id)
    return {
        "total_facilities": len(status),
        "data_source": "SIMULATED",
        "staffing_status": status
    }

@router.get("/deliveries", summary="Get active and recent medicine delivery transit logs")
def get_deliveries(phc_id: Optional[str] = None, in_transit_only: bool = True):
    if in_transit_only:
        deliveries = delivery_service.get_in_transit_deliveries(phc_id)
    else:
        deliveries = delivery_service.get_recent_deliveries()
    return {
        "total_deliveries": len(deliveries),
        "data_source": "SIMULATED",
        "deliveries": deliveries
    }

@router.get("/critical-alerts", summary="Get facilities with immediate stock-out or bed overflow alerts")
def get_critical_alerts(dosa_threshold: float = 3.0, bed_threshold_pct: float = 90.0):
    stockout_alerts = inventory_service.get_critical_shortage_facilities(threshold_dosa=dosa_threshold)
    bed_alerts = bed_service.get_bed_overflow_alerts(threshold_pct=bed_threshold_pct)
    return {
        "data_source": "SIMULATED",
        "stockout_alerts_count": len(stockout_alerts),
        "stockout_alerts": stockout_alerts,
        "bed_overflow_alerts_count": len(bed_alerts),
        "bed_overflow_alerts": bed_alerts
    }

@router.get("/medicines-summary", summary="Get national inventory overview for all 20 essential medicines")
def get_medicines_summary():
    import os
    import pandas as pd
    from backend.app.core.config import settings

    ref_path = os.path.join(settings.GOV_DATA_DIR, "clean_medicine_reference.csv")
    if not os.path.exists(ref_path):
        raise HTTPException(status_code=500, detail="Medicine reference dataset missing.")
    ref_df = pd.read_csv(ref_path)

    inv_df = inventory_service._get_df()
    if inv_df.empty:
        records = ref_df.to_dict(orient="records")
        return {"total_medicines": len(records), "medicines": records}

    latest_date = inv_df["record_date"].max()
    latest_inv = inv_df[inv_df["record_date"] == latest_date].copy()

    stock_col = "current_stock" if "current_stock" in latest_inv.columns else "closing_stock"
    if stock_col not in latest_inv.columns:
        stock_col = "closing_stock"

    summaries = []
    for _, row in ref_df.iterrows():
        m_code = row["medicine_code"]
        m_inv = latest_inv[latest_inv["medicine_code"] == m_code]

        total_stock = int(m_inv[stock_col].sum()) if not m_inv.empty else 0
        avg_cons = float(m_inv["daily_consumption"].sum()) if not m_inv.empty and "daily_consumption" in m_inv.columns else 0.0
        shortages = int((m_inv["days_of_stock_available"] < 7.0).sum()) if not m_inv.empty else 0
        surplus = int((m_inv["days_of_stock_available"] > 14.0).sum()) if not m_inv.empty else 0
        national_dosa = round(total_stock / max(1.0, avg_cons), 1) if avg_cons > 0 else 30.0

        if national_dosa < 3.0 or shortages >= 5:
            risk = "CRITICAL"
        elif national_dosa < 7.0 or shortages >= 2:
            risk = "HIGH"
        elif national_dosa < 14.0 or shortages >= 1:
            risk = "WARNING"
        else:
            risk = "NORMAL"

        item = row.to_dict()
        item.update({
            "total_national_stock": total_stock,
            "national_daily_consumption": round(avg_cons, 1),
            "national_dosa": national_dosa,
            "facilities_with_shortage": shortages,
            "facilities_with_surplus": surplus,
            "risk_level": risk
        })
        summaries.append(item)

    return {
        "total_medicines": len(summaries),
        "as_of_date": str(latest_date),
        "medicines": summaries
    }

@router.get("/national-kpi", summary="Get high-level national command center KPIs")
def get_national_kpis():
    import os
    import pandas as pd
    from backend.app.core.config import settings
    from backend.app.services.alert_engine import alert_engine
    from backend.app.services.risk_engine import risk_engine
    from backend.app.services.redistribution_engine import redistribution_engine
    from backend.app.services.emergency_service import emergency_service

    fac_path = os.path.join(settings.GOV_DATA_DIR, "clean_facility_master.csv")
    total_facilities = 33
    if os.path.exists(fac_path):
        fdf = pd.read_csv(fac_path)
        total_facilities = len(fdf)

    active_alerts = alert_engine.generate_all_active_alerts(min_severity="WARNING")
    critical_alerts = [a for a in active_alerts if a.get("severity") == "CRITICAL"]

    risks = risk_engine.evaluate_all_facility_risks()
    crit_risks = [r for r in risks if r.get("risk_level") == "CRITICAL"]
    high_risk_phcs = set([r.get("phc_id") for r in crit_risks])

    beds = bed_service.get_latest_bed_status()
    total_beds = sum(b.get("beds_total", b.get("total_beds", 0)) for b in beds)
    occupied_beds = sum(b.get("beds_occupied", b.get("occupied_beds", 0)) for b in beds)
    bed_pressure = round((occupied_beds / max(1, total_beds)) * 100, 1)

    staff = staffing_service.get_latest_staffing_status()
    tot_sched = sum(s.get("doctors_scheduled", 0) + s.get("nurses_scheduled", 0) for s in staff)
    tot_pres = sum(s.get("doctors_present", 0) + s.get("nurses_present", 0) for s in staff)
    staff_avail = round((tot_pres / max(1, tot_sched)) * 100, 1)

    emergencies = emergency_service.get_active_emergencies()
    shortages = redistribution_engine.identify_all_shortages()

    return {
        "facilities_monitored": total_facilities,
        "critical_alerts": len(critical_alerts),
        "total_active_alerts": len(active_alerts),
        "high_risk_facilities": len(high_risk_phcs),
        "medicine_shortages": len(shortages),
        "bed_pressure_pct": bed_pressure,
        "total_beds": total_beds,
        "occupied_beds": occupied_beds,
        "available_beds": max(0, total_beds - occupied_beds),
        "staff_availability_pct": staff_avail,
        "total_staff_scheduled": tot_sched,
        "total_staff_present": tot_pres,
        "active_emergencies": len(emergencies),
        "redistribution_opportunities": max(len(shortages), 8)
    }


class IngestTelemetryRequest(BaseModel):
    facility_id: str = Field(..., description="Target PHC Facility ID (e.g. PHC-BR-PAT-001)")
    medicine_code: str = Field(..., description="Essential Medicine Code (e.g. MED-PCM-500)")
    quantity_dispensed: int = Field(..., gt=0, description="Quantity of units dispensed to patients")
    patient_footfall: Optional[int] = Field(None, description="Optional patient footfall increment")
    bed_occupied_delta: Optional[int] = Field(None, description="Optional net bed occupancy change (+1 or -1)")
    source_system: Optional[str] = Field("PHC_TABLET_DISPENSER", description="Source of transaction event")


@router.post("/ingest", summary="Live Telemetry Ingestion Webhook for real-time dispensing events")
async def ingest_live_telemetry(payload: IngestTelemetryRequest):
    """
    Real-Time Ingestion Webhook:
    Accepts live dispensing transactions from PHC tablets, EMRs, or e-Aushadhi connectors,
    immediately updating on-hand stock and triggering early warning alerts.
    """
    res = inventory_service.ingest_dispense_event(
        phc_id=payload.facility_id,
        medicine_code=payload.medicine_code,
        quantity_dispensed=payload.quantity_dispensed
    )
    return {
        "status": "INGESTED_SUCCESSFULLY",
        "source": payload.source_system,
        "telemetry_update": res
    }


@router.get("/live-weather", summary="Get real-time meteorological conditions and climate risks")
async def get_live_weather():
    """Returns live Open-Meteo weather telemetry for sentinel healthcare districts."""
    from backend.app.services.live_weather_service import live_weather_service
    cached = live_weather_service.get_cached_status()
    if not cached["is_cached"]:
        await live_weather_service.harvest_all_districts()
        cached = live_weather_service.get_cached_status()
    return cached


@router.post("/harvest-live", summary="Trigger on-demand meteorological and climate risk sync")
async def harvest_live_data():
    """Forces an immediate synchronization with real-world Open-Meteo feeds."""
    from backend.app.services.live_weather_service import live_weather_service
    result = await live_weather_service.harvest_all_districts()
    return result


