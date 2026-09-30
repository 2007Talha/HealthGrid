"""
Swasthya Records - Early Warning Alert Generation Engine
Consolidates predictions, inventory trajectories, bed occupancy, staffing pressure,
and delivery delays into structured, evidence-grounded alerts.
"""

import time
import uuid
import datetime
import threading

from backend.app.services.risk_engine import risk_engine
from backend.app.services.bed_service import bed_service
from backend.app.services.staffing_service import staffing_service
from backend.app.services.emergency_service import emergency_service


class AlertEngine:
    def __init__(self):
        self._cached_alerts = []
        self._cache_timestamp = 0.0
        self._alert_lock = threading.Lock()

    def clear_cache(self):
        with self._alert_lock:
            self._cached_alerts.clear()
            self._cache_timestamp = 0.0

    def generate_all_active_alerts(self, min_severity="WARNING"):
        """Scans all facility telemetry, forecasts, and logistics to generate active early warnings."""
        now = time.time()
        severity_ranks = {"INFO": 1, "WARNING": 2, "HIGH": 3, "CRITICAL": 4}
        min_rank = severity_ranks.get(min_severity, 2)

        if self._cached_alerts and (now - self._cache_timestamp) < 300.0:
            return [
                a
                for a in self._cached_alerts
                if severity_ranks.get(a.get("severity", "LOW"), 0) >= min_rank
            ]

        with self._alert_lock:
            if self._cached_alerts and (now - self._cache_timestamp) < 300.0:
                return [
                    a
                    for a in self._cached_alerts
                    if severity_ranks.get(a.get("severity", "LOW"), 0) >= min_rank
                ]

            from backend.app.services.facilities_service import facilities_service

            fac_map = {
                f["facility_id"]: f for f in facilities_service.get_all_facilities()
            }

        alerts = []

        # 1. Medicine Stock-Out Risk Alerts
        all_risks = risk_engine.evaluate_all_facility_risks()
        for r in all_risks:
            risk_level = r.get("risk_level", "LOW")
            rank = severity_ranks.get(risk_level, 0)
            if risk_level in ["CRITICAL", "HIGH", "WARNING"]:
                alert_id = f"ALT-MED-{uuid.uuid4().hex[:8].upper()}"

                horizon_val = r.get("projected_stockout_horizon_days")
                dosa_val = float(
                    r.get("days_of_stock_available")
                    if r.get("days_of_stock_available") is not None
                    else 0.0
                )
                safety_val = r.get("safety_stock_threshold") or 100

                if risk_level == "CRITICAL":
                    horizon_str = (
                        f"~{horizon_val:.1f}" if horizon_val is not None else "< 1"
                    )
                    impact = f"Immediate stock-out expected in {horizon_str} days (DOSA: {dosa_val:.1f}d). High risk of treatment failure for acute patients."
                    rec = f"Authorize emergency redistribution transfer from nearest surplus facility in district."
                elif risk_level == "HIGH":
                    impact = f"Stock coverage buffer is below 5 days ({dosa_val:.1f} DOSA). Warehouse restock lead-time exceeds remaining stock."
                    rec = (
                        "Expedite pending shipment or trigger priority buffer reorder."
                    )
                else:
                    impact = f"Stock has fallen below calculated safety buffer ({safety_val:,} units)."
                    rec = "Verify scheduled routine replenishment orders."

                fac_meta = fac_map.get(r.get("phc_id", ""), {})
                now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
                alert = {
                    "alert_id": alert_id,
                    "severity": risk_level,
                    "alert_type": "MEDICINE_STOCKOUT_RISK",
                    "facility_id": r.get("phc_id", ""),
                    "facility_name": r.get("facility_name", ""),
                    "district": fac_meta.get("district_name", r.get("district", "")),
                    "state": fac_meta.get("state_name", r.get("state", "")),
                    "resource_type": "MEDICINE",
                    "resource_id": r.get("medicine_code", ""),
                    "resource_name": r.get("medicine_name", ""),
                    "current_value": float(r.get("current_stock", 0)),
                    "threshold_value": float(safety_val),
                    "days_until_breach": float(
                        horizon_val if horizon_val is not None else dosa_val
                    ),
                    "model_confidence": 0.94,
                    "recommended_action": rec,
                    "recommended_next_step": rec,
                    "evidence_summary": r.get("evidence_summary")
                    or f"Current stock: {r.get('current_stock', 0)} units | DOSA: {dosa_val:.1f} days | Risk: {risk_level}",
                    "projected_impact": impact,
                    "created_at": now_iso,
                    "timestamp": now_iso,
                    "status": "ACTIVE",
                }
                alerts.append(alert)

        # 2. Inpatient Bed Capacity Alerts
        bed_statuses = bed_service.get_latest_bed_status()
        for b in bed_statuses:
            occ_rate = b.get("bed_occupancy_rate_pct", 0.0)
            if occ_rate >= 90.0:
                severity = "CRITICAL" if occ_rate >= 100.0 else "HIGH"
                fac_meta = fac_map.get(b.get("phc_id", ""), {})
                now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
                alert = {
                    "alert_id": f"ALT-BED-{uuid.uuid4().hex[:8].upper()}",
                    "severity": severity,
                    "alert_type": "BED_CAPACITY_RISK",
                    "facility_id": b.get("phc_id", ""),
                    "facility_name": b.get("facility_name", ""),
                    "district": fac_meta.get("district_name", b.get("district", "")),
                    "state": fac_meta.get("state_name", b.get("state", "")),
                    "resource_type": "BED",
                    "resource_id": "BEDS",
                    "resource_name": "Inpatient Functional Beds",
                    "current_value": float(b.get("beds_occupied", 0)),
                    "threshold_value": float(b.get("beds_total", 0)),
                    "days_until_breach": 0.0,
                    "model_confidence": 0.98,
                    "recommended_action": "Divert non-critical admissions to nearest CHC/Sub-divisional hospital.",
                    "recommended_next_step": "Divert non-critical admissions to nearest CHC/Sub-divisional hospital.",
                    "evidence_summary": f"Bed Occupancy: {b.get('beds_occupied')}/{b.get('beds_total')} beds occupied ({occ_rate}% utilization). Available: {b.get('beds_available')} beds.",
                    "projected_impact": "Facility is at or exceeding inpatient capacity; triage delays anticipated for incoming emergency admissions.",
                    "created_at": now_iso,
                    "timestamp": now_iso,
                    "status": "ACTIVE",
                }
                alerts.append(alert)

        # 3. Staff Shortage Alerts
        staff_statuses = staffing_service.get_latest_staffing_status()
        for s in staff_statuses:
            if s.get("doctor_shortage_flag"):
                fac_meta = fac_map.get(s.get("phc_id", ""), {})
                now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
                alert = {
                    "alert_id": f"ALT-STF-{uuid.uuid4().hex[:8].upper()}",
                    "severity": "HIGH",
                    "alert_type": "STAFF_SHORTAGE_RISK",
                    "facility_id": s.get("phc_id", ""),
                    "facility_name": s.get("facility_name", ""),
                    "district": fac_meta.get("district_name", s.get("district", "")),
                    "state": fac_meta.get("state_name", s.get("state", "")),
                    "resource_type": "STAFF",
                    "resource_id": "DOCTORS",
                    "resource_name": "Medical Officers",
                    "current_value": float(s.get("doctors_present", 0)),
                    "threshold_value": float(s.get("doctors_scheduled", 0)),
                    "days_until_breach": 0.0,
                    "model_confidence": 0.95,
                    "recommended_action": "Request temporary duty roster assignment from District Hospital Pool.",
                    "recommended_next_step": "Request temporary duty roster assignment from District Hospital Pool.",
                    "evidence_summary": f"Doctor Roster Shortage: {s.get('doctors_present')} present out of {s.get('doctors_scheduled')} scheduled during active patient surge.",
                    "projected_impact": "OPD wait times elevated; emergency resuscitation coverage compromised.",
                    "created_at": now_iso,
                    "timestamp": now_iso,
                    "status": "ACTIVE",
                }
                alerts.append(alert)

        # 4. Active Outbreak / Emergency Alerts
        emergencies = emergency_service.get_active_emergencies()
        for em in emergencies:
            now_iso = em.get(
                "created_at", datetime.datetime.now(datetime.timezone.utc).isoformat()
            )
            alert = {
                "alert_id": f"ALT-EMG-{uuid.uuid4().hex[:8].upper()}",
                "severity": em.get("severity", "HIGH"),
                "alert_type": "EMERGENCY_OUTBREAK_SURGE",
                "facility_id": "DISTRICT_WIDE",
                "facility_name": f"Districts: {', '.join(em.get('affected_district_ids', []))}",
                "district": ", ".join(em.get("affected_district_ids", [])),
                "state": "Bihar",
                "resource_type": "EMERGENCY",
                "resource_id": em.get("event_type", "SURGE"),
                "resource_name": f"Emergency Scenario ({em.get('event_type')})",
                "current_value": float(em.get("demand_multiplier", 1.0)),
                "threshold_value": 1.0,
                "days_until_breach": 0.0,
                "model_confidence": 0.99,
                "recommended_action": "Place district supply hubs on heightened emergency dispatch readiness.",
                "recommended_next_step": "Place district supply hubs on heightened emergency dispatch readiness.",
                "evidence_summary": f"Active {em.get('event_type')} with {em.get('demand_multiplier')}x demand acceleration across {em.get('facilities_impacted_count', 0)} healthcare facilities.",
                "projected_impact": "Accelerated consumption of essential antipyretics, hydration fluids, and IV antibiotics.",
                "created_at": now_iso,
                "timestamp": now_iso,
                "status": "ACTIVE",
            }
            alerts.append(alert)

        self._cached_alerts = alerts
        self._cache_timestamp = now
        return [
            a
            for a in alerts
            if severity_ranks.get(a.get("severity", "LOW"), 0) >= min_rank
        ]

    def get_alert_by_id(self, alert_id):
        """Retrieves a specific alert by ID or regenerates if cache empty."""
        if not self._cached_alerts:
            self.generate_all_active_alerts()
        for a in self._cached_alerts:
            if a["alert_id"] == alert_id:
                return a
        return None


alert_engine = AlertEngine()
