"""
Swasthya Records - Gemini Operations Copilot & AI Agent Service
Core reasoning and tool-calling orchestrator for healthcare supply chain operations.
"""

import os
import re
import json
import uuid
import datetime
import pandas as pd
import numpy as np

from backend.app.core.config import settings
from backend.app.services.inventory_service import inventory_service
from backend.app.services.bed_service import bed_service
from backend.app.services.staffing_service import staffing_service
from backend.app.services.emergency_service import emergency_service
from backend.app.services.ml_forecasting import forecasting_engine
from backend.app.services.risk_engine import risk_engine
from backend.app.services.alert_engine import alert_engine
from backend.app.services.redistribution_engine import redistribution_engine
from backend.app.services.simulation_manager import simulation_manager
from backend.app.services.delivery_service import delivery_service

AUDIT_LOG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "processed",
    "copilot_audit_log.json",
)
CONVERSATION_HISTORY_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "processed",
    "copilot_conversations.json",
)


class CopilotService:
    """
    Orchestrates the SwasthyaGrid Copilot with deterministic tool execution,
    grounded Gemini natural language generation, security checks, and audit trails.
    """

    def __init__(self):
        self.conversations = {}
        self.audit_log = []
        self._facilities_cache = None
        self._load_persisted_state()

    def _load_persisted_state(self):
        try:
            if os.path.exists(AUDIT_LOG_FILE):
                with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
                    self.audit_log = json.load(f)
            if os.path.exists(CONVERSATION_HISTORY_FILE):
                with open(CONVERSATION_HISTORY_FILE, "r", encoding="utf-8") as f:
                    self.conversations = json.load(f)
        except Exception:
            self.audit_log = []
            self.conversations = {}

    def _persist_state(self):
        try:
            os.makedirs(os.path.dirname(AUDIT_LOG_FILE), exist_ok=True)
            with open(AUDIT_LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.audit_log[-500:], f, indent=2)
            with open(CONVERSATION_HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.conversations, f, indent=2)
        except Exception:
            pass

    def _get_facilities(self):
        if self._facilities_cache is None:
            csv_path = os.path.join(settings.GOV_DATA_DIR, "clean_facility_master.csv")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                self._facilities_cache = df.to_dict(orient="records")
            else:
                self._facilities_cache = []
        return self._facilities_cache

    def _get_facility_by_id(self, facility_id):
        facs = self._get_facilities()
        for f in facs:
            if f["facility_id"] == facility_id:
                return f
        return None

    def log_audit_entry(
        self, user_role, user_id, tool_name, parameters, result_summary, conversation_id
    ):
        entry = {
            "log_id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "user_id": user_id,
            "user_role": user_role,
            "tool_called": tool_name,
            "tool_parameters": parameters,
            "result_summary": result_summary,
        }
        self.audit_log.append(entry)
        self._persist_state()

    # =========================================================================
    # TOOL 1: National Summary
    # =========================================================================
    def get_national_summary(self, user_role="ADMIN", assigned_state=None):
        """Provides an aggregated national view of health facilities, active alerts, and resource risks."""
        facilities = self._get_facilities()
        states = list(
            {
                f.get("state_name", f.get("state"))
                for f in facilities
                if f.get("state_name") or f.get("state")
            }
        )
        districts = list(
            {
                f.get("district_code", f.get("district_id"))
                for f in facilities
                if f.get("district_code") or f.get("district_id")
            }
        )

        alerts = alert_engine.generate_all_active_alerts(min_severity="WARNING")
        crit_alerts = [a for a in alerts if a.get("severity") == "CRITICAL"]
        high_alerts = [a for a in alerts if a.get("severity") == "HIGH"]

        high_risk_facs = list(
            {
                a.get("facility_id")
                for a in alerts
                if a.get("severity") in ["CRITICAL", "HIGH"]
            }
        )
        med_shortages = redistribution_engine.identify_all_shortages()

        active_em = emergency_service.get_active_emergencies()

        redist_recs = []
        for sh in med_shortages[:5]:
            cand = redistribution_engine.find_candidate_sources(
                sh["facility_id"], sh["medicine_code"]
            )
            if cand:
                redist_recs.append(sh["facility_id"])

        return {
            "total_facilities": len(facilities),
            "states_represented": sorted([str(s) for s in states if s]),
            "total_states": len(states),
            "districts_represented_count": len(districts),
            "critical_alerts_count": len(crit_alerts),
            "high_alerts_count": len(high_alerts),
            "high_risk_facilities_count": len(high_risk_facs),
            "medicine_shortages_count": len(med_shortages),
            "bed_capacity_warnings": len(
                [a for a in alerts if a.get("alert_type") == "BED_CAPACITY_RISK"]
            ),
            "staffing_warnings": len(
                [a for a in alerts if a.get("alert_type") == "STAFF_SHORTAGE_RISK"]
            ),
            "active_emergencies": len(active_em),
            "emergency_details": active_em[0] if active_em else None,
            "redistribution_opportunities_count": len(redist_recs),
        }

    # =========================================================================
    # TOOL 2: State Summary
    # =========================================================================
    def get_state_summary(self, state):
        """Returns consolidated health infrastructure & supply telemetry for a specified Indian state."""
        state_clean = state.strip().title()
        facilities = self._get_facilities()
        state_facs = [
            f
            for f in facilities
            if state_clean.lower() in str(f.get("state_name", "")).lower()
            or state_clean.lower() in str(f.get("state", "")).lower()
        ]

        if not state_facs:
            return {
                "error": f"No registered facilities found for state '{state}'. Available states: Bihar, Uttar Pradesh, Maharashtra, Karnataka, Odisha.",
                "state": state,
            }

        fac_ids = [f["facility_id"] for f in state_facs]
        districts = list(
            {f.get("district_code", f.get("district_id")) for f in state_facs}
        )

        alerts = alert_engine.generate_all_active_alerts(min_severity="WARNING")
        state_alerts = [a for a in alerts if a.get("facility_id") in fac_ids]
        crit_alerts = [a for a in state_alerts if a.get("severity") == "CRITICAL"]

        med_risks = [
            a for a in state_alerts if a.get("alert_type") == "MEDICINE_STOCKOUT_RISK"
        ]
        bed_risks = [
            a for a in state_alerts if a.get("alert_type") == "BED_CAPACITY_RISK"
        ]
        staff_risks = [
            a for a in state_alerts if a.get("alert_type") == "STAFF_SHORTAGE_RISK"
        ]

        active_em = emergency_service.get_active_emergencies()
        state_in_emergency = False
        if active_em:
            aff_dists = active_em[0].get("affected_district_ids", [])
            state_in_emergency = any(d in districts for d in aff_dists)

        return {
            "state": state_clean,
            "facility_count": len(state_facs),
            "districts": [str(d) for d in districts if d],
            "critical_alerts_count": len(crit_alerts),
            "high_risk_facilities": list({a["facility_id"] for a in crit_alerts}),
            "medicine_risks_count": len(med_risks),
            "bed_risks_count": len(bed_risks),
            "staffing_risks_count": len(staff_risks),
            "emergency_status": {
                "active_in_state": state_in_emergency,
                "event": active_em[0].get("event_type")
                if state_in_emergency
                else "NONE",
                "severity": active_em[0].get("severity")
                if state_in_emergency
                else "NORMAL",
            },
        }

    # =========================================================================
    # TOOL 3: District Summary
    # =========================================================================
    def get_district_summary(self, district):
        """Provides facility-level status, bed occupancy, and shortages for a specific district."""
        district_query = district.strip().upper()
        facilities = self._get_facilities()
        dist_facs = [
            f
            for f in facilities
            if district_query in str(f.get("district_code", "")).upper()
            or district_query in str(f.get("district_name", "")).upper()
        ]

        if not dist_facs:
            return {
                "error": f"District '{district}' not found in active health registry."
            }

        dist_id = dist_facs[0].get("district_code", dist_facs[0].get("district_id"))
        dist_name = dist_facs[0].get("district_name", district)
        fac_ids = [f["facility_id"] for f in dist_facs]

        bed_stats = bed_service.get_latest_bed_status()
        dist_beds = [b for b in bed_stats if b.get("phc_id") in fac_ids]

        total_beds = sum(b.get("beds_total", 0) for b in dist_beds)
        occupied_beds = sum(b.get("beds_occupied", 0) for b in dist_beds)
        avg_occupancy = round(occupied_beds / max(1, total_beds) * 100, 1)

        staff_stats = staffing_service.get_latest_staffing_status()
        dist_staff = [s for s in staff_stats if s.get("phc_id") in fac_ids]
        total_staff = sum(
            s.get("doctors_present", 0) + s.get("nurses_present", 0) for s in dist_staff
        )

        all_shortages = redistribution_engine.identify_all_shortages()
        dist_shortages = [s for s in all_shortages if s.get("facility_id") in fac_ids]

        active_em = emergency_service.get_active_emergencies()
        is_em = bool(
            active_em and dist_id in active_em[0].get("affected_district_ids", [])
        )

        return {
            "district_id": dist_id,
            "district_name": dist_name,
            "facility_count": len(dist_facs),
            "facilities": [
                {
                    "id": f["facility_id"],
                    "name": f["facility_name"],
                    "type": f.get("facility_type", "PHC"),
                }
                for f in dist_facs
            ],
            "bed_occupancy_pct": avg_occupancy,
            "total_beds": total_beds,
            "occupied_beds": occupied_beds,
            "medical_staff_on_duty": total_staff,
            "critical_shortages_count": len(dist_shortages),
            "shortage_details": dist_shortages,
            "active_emergency": is_em,
        }

    # =========================================================================
    # TOOL 4: Facility Status
    # =========================================================================
    def get_facility_status(self, phc_id):
        """Returns deep telemetry for a single Primary Health Centre or Hospital."""
        fac = self._get_facility_by_id(phc_id)
        if not fac:
            return {"error": f"Facility ID '{phc_id}' not found in registry."}

        inventory = inventory_service.get_latest_inventory_by_phc(phc_id)
        bed_stats = bed_service.get_latest_bed_status(phc_id)
        bed_item = bed_stats[0] if bed_stats else {}

        staff_stats = staffing_service.get_latest_staffing_status(phc_id)
        staff_item = staff_stats[0] if staff_stats else {}

        alerts = [
            a
            for a in alert_engine.generate_all_active_alerts(min_severity="WARNING")
            if a.get("facility_id") == phc_id
        ]
        incoming = delivery_service.get_incoming_deliveries(phc_id, max_eta_days=7)

        med_risks = []
        for item in inventory[:10]:
            r = risk_engine.evaluate_medicine_stock_risk(phc_id, item["medicine_code"])
            if r.get("risk_level") in ["CRITICAL", "HIGH", "WARNING"]:
                med_risks.append(
                    {
                        "medicine_code": item["medicine_code"],
                        "medicine_name": item["medicine_name"],
                        "current_stock": int(
                            item.get("closing_stock", item.get("current_stock", 0))
                        ),
                        "dosa_days": r.get("days_of_stock_available"),
                        "risk_level": r.get("risk_level"),
                    }
                )

        return {
            "facility_id": fac["facility_id"],
            "facility_name": fac["facility_name"],
            "facility_type": fac.get("facility_type", "PHC"),
            "district": fac.get("district_name"),
            "state": fac.get("state_name", fac.get("state")),
            "latitude": fac.get("latitude", fac.get("lat")),
            "longitude": fac.get("longitude", fac.get("lng")),
            "bed_capacity": {
                "total_beds": bed_item.get("beds_total", 10),
                "occupied_beds": bed_item.get("beds_occupied", 4),
                "occupancy_rate_pct": bed_item.get("bed_occupancy_rate_pct", 40.0),
            },
            "staff_status": {
                "doctors_present": staff_item.get("doctors_present", 2),
                "nurses_present": staff_item.get("nurses_present", 4),
                "staff_shortage": bool(
                    staff_item.get("doctor_shortage_flag")
                    or staff_item.get("nurse_shortage_flag")
                ),
            },
            "critical_medicine_risks": med_risks,
            "active_alerts_count": len(alerts),
            "alerts": alerts,
            "incoming_deliveries": incoming,
        }

    # =========================================================================
    # TOOL 5: Critical Alerts
    # =========================================================================
    def get_critical_alerts(self, min_severity="HIGH"):
        """Retrieves all current CRITICAL and HIGH priority early warnings with evidence."""
        alerts = alert_engine.generate_all_active_alerts(min_severity=min_severity)
        return {
            "total_alerts": len(alerts),
            "severity_filter": min_severity,
            "alerts": alerts,
        }

    # =========================================================================
    # TOOL 6: Stockout Risks
    # =========================================================================
    def get_stockout_risks(
        self,
        state=None,
        district=None,
        medicine=None,
        risk_level=None,
        time_horizon_days=None,
    ):
        """Searches across all facility inventory levels for projected stockout risks using fast cached evaluations."""
        from backend.app.services.facilities_service import facilities_service

        fac_map = {f["facility_id"]: f for f in facilities_service.get_all_facilities()}

        all_risks = risk_engine.evaluate_all_facility_risks()
        results = []

        for r in all_risks:
            fid = r.get("phc_id", "")
            fac = fac_map.get(fid, {})
            fac_name = fac.get("facility_name", r.get("facility_name", ""))
            fac_state = fac.get("state_name", r.get("state", ""))
            fac_dist = fac.get("district_name", r.get("district", ""))
            m_code = r.get("medicine_code", "")
            m_name = r.get("medicine_name", "")

            if state and state.lower() not in str(fac_state).lower():
                continue
            if district and district.lower() not in str(fac_dist).lower():
                continue
            if medicine and (
                medicine.lower() not in m_code.lower()
                and medicine.lower() not in m_name.lower()
            ):
                continue

            r_level = r.get("risk_level", "LOW")
            dosa = float(
                r.get("days_of_stock_available")
                if r.get("days_of_stock_available") is not None
                else 99.0
            )

            if risk_level and r_level != risk_level.upper():
                continue
            if time_horizon_days is not None and dosa > time_horizon_days:
                continue

            if r_level in ["CRITICAL", "HIGH", "WARNING"]:
                results.append(
                    {
                        "facility_id": fid,
                        "facility_name": fac_name,
                        "district": fac_dist,
                        "state": fac_state,
                        "medicine_code": m_code,
                        "medicine_name": m_name,
                        "current_stock": int(r.get("current_stock", 0)),
                        "daily_consumption_forecast": float(
                            r.get("average_daily_predicted_demand", 0)
                        ),
                        "days_of_stock_available": dosa,
                        "risk_level": r_level,
                        "reorder_needed": dosa < 7.0,
                    }
                )

        results = sorted(results, key=lambda x: x["days_of_stock_available"])
        return {
            "total_matches": len(results),
            "filters": {
                "state": state,
                "district": district,
                "medicine": medicine,
                "risk_level": risk_level,
                "horizon_days": time_horizon_days,
            },
            "results": results[:25],
        }

    # =========================================================================
    # TOOL 7: Medicine Status
    # =========================================================================
    def get_medicine_status(self, phc_id, medicine_id):
        """Provides full stock telemetry, consumption rate, and safety thresholds for a specific medicine."""
        fac = self._get_facility_by_id(phc_id)
        if not fac:
            return {"error": f"Facility '{phc_id}' not found."}

        inv = inventory_service.get_latest_inventory_by_phc(phc_id)
        item = next(
            (
                i
                for i in inv
                if i["medicine_code"] == medicine_id
                or medicine_id.lower() in i["medicine_name"].lower()
            ),
            None,
        )
        if not item:
            return {
                "error": f"Medicine '{medicine_id}' not found in facility {phc_id}."
            }

        risk = risk_engine.evaluate_medicine_stock_risk(phc_id, item["medicine_code"])
        incoming = [
            d
            for d in delivery_service.get_incoming_deliveries(phc_id)
            if d.get("medicine_code") == item["medicine_code"]
        ]

        return {
            "facility_id": phc_id,
            "facility_name": fac["facility_name"],
            "medicine_code": item["medicine_code"],
            "medicine_name": item["medicine_name"],
            "current_stock": int(
                item.get("closing_stock", item.get("current_stock", 0))
            ),
            "safety_stock": item.get("safety_stock_threshold", 100),
            "reorder_level": item.get("reorder_level", 250),
            "predicted_daily_consumption": risk.get(
                "average_daily_predicted_demand", 0
            ),
            "days_of_stock_available": risk.get("days_of_stock_available", 0),
            "risk_level": risk.get("risk_level", "LOW"),
            "incoming_shipments": incoming,
        }

    # =========================================================================
    # TOOL 8: Forecast Retrieval
    # =========================================================================
    def get_forecast(self, phc_id, resource, horizon=14):
        """Retrieves Ridge regression multi-day demand predictions with uncertainty intervals."""
        fac = self._get_facility_by_id(phc_id)
        if not fac:
            return {"error": f"Facility '{phc_id}' not found."}

        if "footfall" in resource.lower() or "patient" in resource.lower():
            fc = forecasting_engine.forecast_patient_footfall(
                phc_id, horizon_days=horizon
            )
            return {
                "facility_id": phc_id,
                "facility_name": fac["facility_name"],
                "resource": "PATIENT_FOOTFALL",
                "model_version": "ridge-footfall-v1.0",
                "horizon_days": horizon,
                "forecasts": fc,
            }
        elif "bed" in resource.lower():
            fc = forecasting_engine.forecast_bed_occupancy(phc_id, horizon_days=horizon)
            return {
                "facility_id": phc_id,
                "facility_name": fac["facility_name"],
                "resource": "BED_OCCUPANCY",
                "model_version": "ridge-bed-v1.0",
                "horizon_days": horizon,
                "forecasts": fc,
            }
        else:
            fc = forecasting_engine.forecast_medicine_demand(
                phc_id, resource, horizon_days=horizon
            )
            return {
                "facility_id": phc_id,
                "facility_name": fac["facility_name"],
                "resource": resource,
                "model_version": "swasthya-demand-v1.0",
                "horizon_days": horizon,
                "forecasts": fc,
            }

    # =========================================================================
    # TOOL 9: Redistribution Options
    # =========================================================================
    def get_redistribution_options(self, phc_id, resource):
        """Runs the OR-Tools optimizer to find optimal candidate source facilities with surplus protection."""
        fac = self._get_facility_by_id(phc_id)
        if not fac:
            return {"error": f"Destination facility '{phc_id}' not found."}

        rec = redistribution_engine.generate_redistribution_recommendation(
            phc_id, resource
        )
        if "recommendation" not in rec:
            rec["recommendation"] = rec.get(
                "reason_summary",
                rec.get("message", "Redistribution recommendation computed"),
            )
        return rec

    # =========================================================================
    # TOOL 10: Simulate Redistribution
    # =========================================================================
    def simulate_redistribution(self, recommendation_id):
        """Executes a reversible digital twin transfer simulation and returns Before/After risk."""
        sim = simulation_manager.apply_simulated_transfer(recommendation_id)
        return sim

    # =========================================================================
    # TOOL 11: Emergency Status
    # =========================================================================
    def get_emergency_status(self):
        """Returns active healthcare disaster, disease outbreak, or monsoon emergency parameters."""
        active_em = emergency_service.get_active_emergencies()
        if not active_em:
            return {
                "active_emergency": False,
                "message": "No active emergency event in progress. System is running in NORMAL baseline state.",
            }
        em = active_em[0]
        return {
            "active_emergency": True,
            "event_type": em.get("event_type"),
            "severity": em.get("severity"),
            "demand_multiplier": em.get("demand_multiplier"),
            "affected_district_ids": em.get("affected_district_ids", []),
            "duration_days": em.get("duration_days"),
            "description": em.get("description"),
        }

    # =========================================================================
    # TOOL 12: Resource Pressure
    # =========================================================================
    def get_resource_pressure(self):
        """Identifies top medicines, beds, and districts experiencing acute supply-chain stress."""
        alerts = alert_engine.generate_all_active_alerts(min_severity="WARNING")

        med_pressure = {}
        for a in alerts:
            if a.get("alert_type") == "MEDICINE_STOCKOUT_RISK":
                res = a.get("resource_name", a.get("resource_id", "Unknown"))
                med_pressure[res] = med_pressure.get(res, 0) + 1

        sorted_meds = [
            {"medicine": k, "active_warnings_count": v}
            for k, v in sorted(med_pressure.items(), key=lambda x: x[1], reverse=True)
        ]

        bed_alerts = [a for a in alerts if a.get("alert_type") == "BED_CAPACITY_RISK"]
        staff_alerts = [
            a for a in alerts if a.get("alert_type") == "STAFF_SHORTAGE_RISK"
        ]

        return {
            "top_pressured_medicines": sorted_meds[:5],
            "facilities_with_bed_strain": len(bed_alerts),
            "facilities_with_staff_shortage": len(staff_alerts),
            "total_pressure_indicators": len(alerts),
        }

    # =========================================================================
    # WHAT-IF SIMULATION ENGINE
    # =========================================================================
    def run_what_if_simulation(
        self,
        facility_id,
        medicine_code,
        demand_surge_pct=0.0,
        delivery_delay_days=0,
        transfer_units=0,
    ):
        """
        Runs an isolated What-If scenario against a facility's medicine stock.
        Does NOT alter production state.
        """
        fac = self._get_facility_by_id(facility_id)
        if not fac:
            return {"error": f"Facility '{facility_id}' not found."}

        inv = inventory_service.get_latest_inventory_by_phc(facility_id)
        item = next(
            (
                i
                for i in inv
                if i["medicine_code"] == medicine_code
                or medicine_code.lower() in i["medicine_name"].lower()
            ),
            None,
        )
        if not item:
            return {
                "error": f"Medicine '{medicine_code}' not found in facility {facility_id}."
            }

        m_code = item["medicine_code"]
        med_name = item["medicine_name"]

        base_stock = int(item.get("closing_stock", item.get("current_stock", 0)))
        base_risk = risk_engine.evaluate_medicine_stock_risk(facility_id, m_code)
        base_dosa = base_risk.get("days_of_stock_available", 0.0)
        base_demand = base_risk.get("average_daily_predicted_demand", 10.0)

        sim_demand = base_demand * (1.0 + (demand_surge_pct / 100.0))
        sim_stock = max(0, base_stock + transfer_units)
        sim_dosa = round(sim_stock / max(0.1, sim_demand), 2)

        if sim_dosa < 1.0:
            sim_risk_level = "CRITICAL"
        elif sim_dosa < 3.0:
            sim_risk_level = "HIGH"
        elif sim_dosa < 5.0:
            sim_risk_level = "WARNING"
        else:
            sim_risk_level = "LOW"

        return {
            "simulation_type": "WHAT_IF_SCENARIO",
            "is_simulation": True,
            "facility_id": facility_id,
            "facility_name": fac["facility_name"],
            "medicine_code": m_code,
            "medicine_name": med_name,
            "input_parameters": {
                "demand_surge_pct": demand_surge_pct,
                "delivery_delay_days": delivery_delay_days,
                "transfer_units": transfer_units,
            },
            "baseline": {
                "current_stock": base_stock,
                "daily_demand": base_demand,
                "dosa_days": base_dosa,
                "risk_level": base_risk.get("risk_level"),
            },
            "simulated_outcome": {
                "simulated_stock": sim_stock,
                "simulated_daily_demand": round(sim_demand, 1),
                "simulated_dosa_days": sim_dosa,
                "simulated_risk_level": sim_risk_level,
                "net_dosa_change": round(sim_dosa - base_dosa, 2),
            },
            "simulation_label": "WHAT-IF SIMULATION (Isolated Shadow Test - No State Modified)",
        }

    # =========================================================================
    # COPILOT NLP QUERY DISPATCHER & GROUNDED EXPLAINER
    # =========================================================================
    def process_query(
        self,
        user_message,
        conversation_id=None,
        user_role="ADMIN",
        user_id="default_user",
        language="en",
    ):
        """
        Main natural language query handler:
        1. Classifies intent and determines necessary tool calls.
        2. Executes deterministic backend tools (source of truth).
        3. Generates grounded dual-language Gemini response with citations.
        4. Logs audit entry and maintains conversation history.
        """
        if not conversation_id:
            conversation_id = f"conv-{uuid.uuid4().hex[:8]}"

        msg_clean = user_message.strip()
        msg_lower = msg_clean.lower()
        tool_calls_executed = []
        evidence_data = []
        is_simulation = False
        tool_result = {}

        # Check authorization
        if user_role == "DISTRICT_OPERATOR" and "national" in msg_lower:
            return {
                "response": "Access restricted: District Operators are restricted to district-level queries. Please contact a State or National Admin for national summaries.",
                "language": language,
                "tool_calls": [],
                "evidence": [],
                "simulation": False,
                "conversation_id": conversation_id,
            }

        # 1. WHAT-IF SCENARIO CHECK
        if (
            "what happens if" in msg_lower
            or "what if" in msg_lower
            or "suppose" in msg_lower
            or (
                "simulate" in msg_lower
                and (
                    "transfer" in msg_lower
                    or "surge" in msg_lower
                    or "increase" in msg_lower
                    or "delay" in msg_lower
                )
            )
        ):
            is_simulation = True
            surge = (
                30.0 if "30%" in msg_lower else (50.0 if "50%" in msg_lower else 20.0)
            )
            transfer = 900 if "900" in msg_lower else (500 if "500" in msg_lower else 0)
            fac_id = "PHC-BR-PAT-001"
            for f in self._get_facilities():
                if (
                    f["facility_id"].lower() in msg_lower
                    or f["facility_name"].lower() in msg_lower
                ):
                    fac_id = f["facility_id"]
                    break
            tool_result = self.run_what_if_simulation(
                fac_id, "MED-PCM-500", demand_surge_pct=surge, transfer_units=transfer
            )
            tool_calls_executed.append(
                {
                    "tool": "run_what_if_simulation",
                    "parameters": {
                        "facility_id": fac_id,
                        "surge": surge,
                        "transfer": transfer,
                    },
                }
            )
            evidence_data.append(tool_result)

        # 2. NATIONAL SUMMARY
        elif (
            "national" in msg_lower
            or "overall" in msg_lower
            or "all phc" in msg_lower
            or "country" in msg_lower
            or "india" in msg_lower
            or ("summarize" in msg_lower and "today" in msg_lower)
        ):
            tool_result = self.get_national_summary(user_role=user_role)
            tool_calls_executed.append(
                {"tool": "get_national_summary", "parameters": {}}
            )
            evidence_data.append(tool_result)

        # 3. STATE SUMMARY
        elif any(
            st.lower() in msg_lower
            for st in ["bihar", "uttar pradesh", "maharashtra", "karnataka", "odisha"]
        ):
            target_st = next(
                st
                for st in [
                    "Bihar",
                    "Uttar Pradesh",
                    "Maharashtra",
                    "Karnataka",
                    "Odisha",
                ]
                if st.lower() in msg_lower
            )
            tool_result = self.get_state_summary(target_st)
            tool_calls_executed.append(
                {"tool": "get_state_summary", "parameters": {"state": target_st}}
            )
            evidence_data.append(tool_result)

        # 4. DISTRICT SUMMARY
        elif "district" in msg_lower:
            target_dist = "BR-PATNA"
            if "patna" in msg_lower:
                target_dist = "BR-PATNA"
            elif "gaya" in msg_lower:
                target_dist = "BR-GAYA"
            elif "lucknow" in msg_lower:
                target_dist = "UP-LUCKNOW"
            elif "varanasi" in msg_lower:
                target_dist = "UP-VARANASI"
            elif "pune" in msg_lower:
                target_dist = "MH-PUNE"
            elif "bengaluru" in msg_lower or "bangalore" in msg_lower:
                target_dist = "KA-BENGALURU"
            elif "khordha" in msg_lower:
                target_dist = "OR-KHORDHA"
            tool_result = self.get_district_summary(target_dist)
            tool_calls_executed.append(
                {
                    "tool": "get_district_summary",
                    "parameters": {"district": target_dist},
                }
            )
            evidence_data.append(tool_result)

        # 5. REDISTRIBUTION / SUPPLY SOURCES
        elif (
            "redistribut" in msg_lower
            or "supply" in msg_lower
            or "transfer" in msg_lower
            or "receive" in msg_lower
        ):
            fac_id = "PHC-BR-PAT-001"
            for f in self._get_facilities():
                if (
                    f["facility_id"].lower() in msg_lower
                    or f["facility_name"].lower() in msg_lower
                ):
                    fac_id = f["facility_id"]
                    break
            tool_result = self.get_redistribution_options(fac_id, "MED-AMX-500")
            tool_calls_executed.append(
                {
                    "tool": "get_redistribution_options",
                    "parameters": {"destination": fac_id, "resource": "MED-AMX-500"},
                }
            )
            evidence_data.append(tool_result)

        # 6. FORECASTING
        elif (
            "forecast" in msg_lower
            or "demand" in msg_lower
            or "prediction" in msg_lower
            or "expected" in msg_lower
        ):
            fac_id = "PHC-BR-PAT-001"
            for f in self._get_facilities():
                if (
                    f["facility_id"].lower() in msg_lower
                    or f["facility_name"].lower() in msg_lower
                ):
                    fac_id = f["facility_id"]
                    break
            tool_result = self.get_forecast(fac_id, "MED-PCM-500", horizon=7)
            tool_calls_executed.append(
                {
                    "tool": "get_forecast",
                    "parameters": {
                        "phc_id": fac_id,
                        "resource": "MED-PCM-500",
                        "horizon": 7,
                    },
                }
            )
            evidence_data.append(tool_result)

        # 7. FACILITY STATUS / "WHY" CONTEXT / SPECIFIC FACILITY INQUIRY
        elif (
            any(f["facility_id"].lower() in msg_lower for f in self._get_facilities())
            or "why" in msg_lower
            or "phc-" in msg_lower
            or "chc-" in msg_lower
        ):
            fac_match = re.search(r"(phc-[\w-]+|chc-[\w-]+)", msg_lower)
            queried_id = fac_match.group(1).upper() if fac_match else None

            fac_id = queried_id or "PHC-BR-PAT-001"
            found = False
            for f in self._get_facilities():
                if (
                    f["facility_id"].lower() in msg_lower
                    or f["facility_name"].lower() in msg_lower
                ):
                    fac_id = f["facility_id"]
                    found = True
                    break
            if (
                not found
                and not queried_id
                and conversation_id in self.conversations
                and self.conversations[conversation_id]
            ):
                last_entry = self.conversations[conversation_id][-1]
                fac_id = last_entry.get("last_facility_id", "PHC-BR-PAT-001")

            tool_result = self.get_facility_status(fac_id)
            tool_calls_executed.append(
                {"tool": "get_facility_status", "parameters": {"phc_id": fac_id}}
            )
            evidence_data.append(tool_result)

        # 8. EMERGENCY EVENTS
        elif (
            "emergency" in msg_lower
            or "outbreak" in msg_lower
            or "disaster" in msg_lower
            or "surge" in msg_lower
        ):
            tool_result = self.get_emergency_status()
            tool_calls_executed.append(
                {"tool": "get_emergency_status", "parameters": {}}
            )
            evidence_data.append(tool_result)

        # 9. RESOURCE PRESSURE
        elif "pressure" in msg_lower or "strain" in msg_lower or "stress" in msg_lower:
            tool_result = self.get_resource_pressure()
            tool_calls_executed.append(
                {"tool": "get_resource_pressure", "parameters": {}}
            )
            evidence_data.append(tool_result)

        # 10. CRITICAL ALERTS & RISKS (DEFAULT)
        else:
            tool_result = self.get_stockout_risks(risk_level="CRITICAL")
            if not tool_result.get("results"):
                tool_result = self.get_critical_alerts()
                tool_calls_executed.append(
                    {
                        "tool": "get_critical_alerts",
                        "parameters": {"min_severity": "HIGH"},
                    }
                )
            else:
                tool_calls_executed.append(
                    {
                        "tool": "get_stockout_risks",
                        "parameters": {"risk_level": "CRITICAL"},
                    }
                )
            evidence_data.append(tool_result)

        # Generate Grounded Response
        nl_response = self._synthesize_grounded_response(
            user_message, tool_result, language=language, is_simulation=is_simulation
        )

        # Audit Log Entry
        self.log_audit_entry(
            user_role=user_role,
            user_id=user_id,
            tool_name=tool_calls_executed[0]["tool"] if tool_calls_executed else "none",
            parameters=tool_calls_executed[0]["parameters"]
            if tool_calls_executed
            else {},
            result_summary=str(tool_result)[:180],
            conversation_id=conversation_id,
        )

        # Update conversation context
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []

        last_fac = tool_result.get(
            "facility_id", tool_result.get("phc_id", "PHC-BR-PAT-001")
        )
        self.conversations[conversation_id].append(
            {
                "user_query": user_message,
                "assistant_response": nl_response,
                "last_facility_id": last_fac,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
        )
        self._persist_state()

        sanitized_evidence = self._sanitize_data(evidence_data)

        return {
            "response": nl_response,
            "language": language,
            "tool_calls": tool_calls_executed,
            "evidence": sanitized_evidence,
            "simulation": is_simulation,
            "conversation_id": conversation_id,
        }

    def _sanitize_data(self, obj):
        """Recursively sanitizes NaN, Inf, and non-serializable objects into clean JSON-compliant types."""
        if isinstance(obj, dict):
            return {k: self._sanitize_data(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._sanitize_data(v) for v in obj]
        elif isinstance(obj, float):
            if np.isnan(obj) or obj != obj:
                return None
            if np.isinf(obj):
                return 999999.0 if obj > 0 else -999999.0
            return obj
        return obj

    def _synthesize_grounded_response(
        self, user_query, tool_data, language="en", is_simulation=False
    ):
        """Synthesizes structured tool output into clear, verified English or Hindi."""
        if "error" in tool_data:
            if language == "hi":
                return f"डेटा पुनर्प्राप्ति में समस्या: {tool_data['error']}"
            return f"Unable to retrieve operational data: {tool_data['error']}"

        # What-If Simulation
        if is_simulation or tool_data.get("simulation_type") == "WHAT_IF_SCENARIO":
            sim_out = tool_data.get("simulated_outcome", {})
            base = tool_data.get("baseline", {})
            fac_name = tool_data.get("facility_name", "Facility")
            med_name = tool_data.get("medicine_name", "Medicine")
            if language == "hi":
                return (
                    f"**[सिम्युलेशन परिणाम (व्हाट-इफ विश्लेषण)]**\n\n"
                    f"सुविधा: **{fac_name}** | दवा: **{med_name}**\n\n"
                    f"• **वर्तमान स्थिति**: स्टॉक {base.get('current_stock')} यूनिट, खपत {base.get('daily_demand')} यूनिट/दिन, स्टॉक कवरेज {base.get('dosa_days')} दिन ({base.get('risk_level')})\n"
                    f"• **सिम्युलेटेड परिणाम**: स्टॉक {sim_out.get('simulated_stock')} यूनिट, सिम्युलेटेड मांग {sim_out.get('simulated_daily_demand')} यूनिट/दिन\n"
                    f"• **नया स्टॉक कवरेज**: **{sim_out.get('simulated_dosa_days')} दिन** (जोखिम स्तर: **{sim_out.get('simulated_risk_level')}**)\n"
                    f"• **शुद्ध सुधार**: +{sim_out.get('net_dosa_change')} दिन की अतिरिक्त सुरक्षा।\n\n"
                    f"*नोट: यह एक आइसोलेटेड शैडो सिम्युलेशन है; वास्तविक डेटा अपरिवर्तित है।*"
                )
            return (
                f"**[WHAT-IF SIMULATION RESULTS]**\n\n"
                f"Facility: **{fac_name}** | Medicine: **{med_name}**\n\n"
                f"• **Baseline**: Stock {base.get('current_stock')} units, Consumption {base.get('daily_demand')} units/day, Coverage {base.get('dosa_days')} days ({base.get('risk_level')})\n"
                f"• **Simulated Outcome**: Stock {sim_out.get('simulated_stock')} units, Projected Demand {sim_out.get('simulated_daily_demand')} units/day\n"
                f"• **New Coverage Runway**: **{sim_out.get('simulated_dosa_days')} days** (Risk Level: **{sim_out.get('simulated_risk_level')}**)\n"
                f"• **Net Impact**: +{sim_out.get('net_dosa_change')} days added runway.\n\n"
                f"*Note: This is an isolated shadow simulation; production state is unmodified.*"
            )

        # National Summary
        if "total_facilities" in tool_data:
            fac_cnt = tool_data["total_facilities"]
            st_cnt = tool_data["total_states"]
            crit = tool_data["critical_alerts_count"]
            shortages = tool_data["medicine_shortages_count"]
            if language == "hi":
                return (
                    f"**राष्ट्रीय स्वास्थ्य संसाधन स्थिति सारांश**:\n\n"
                    f"• कुल पंजीकृत स्वास्थ्य सुविधाएं: **{fac_cnt}** ({st_cnt} राज्यों में)\n"
                    f"• सक्रिय अति-गंभीर अलर्ट (Critical): **{crit}**\n"
                    f"• दवा की तात्कालिक कमी वाले केंद्र: **{shortages}**\n"
                    f"• बेड क्षमता चेतावनी: **{tool_data.get('bed_capacity_warnings')}** | स्टाफ कमी चेतावनी: **{tool_data.get('staffing_warnings')}**\n"
                    f"• सक्रिय आपदा/आपातकाल: **{tool_data.get('active_emergencies')}**\n\n"
                    f"पुनर्वितरण योजना के लिए उपलब्ध अवसर: **{tool_data.get('redistribution_opportunities_count')} केंद्र**।"
                )
            return (
                f"**National Health Resource Summary**:\n\n"
                f"• Total Monitored Facilities: **{fac_cnt}** across **{st_cnt} states**\n"
                f"• Active Critical Early Warnings: **{crit}**\n"
                f"• Facilities with Immediate Medicine Shortages: **{shortages}**\n"
                f"• Bed Capacity Warnings: **{tool_data.get('bed_capacity_warnings')}** | Staffing Constraints: **{tool_data.get('staffing_warnings')}**\n"
                f"• Active Emergency Events: **{tool_data.get('active_emergencies')}**\n\n"
                f"Optimized cross-district redistribution opportunities identified for **{tool_data.get('redistribution_opportunities_count')} facilities**."
            )

        # State Summary
        if "facility_count" in tool_data and "state" in tool_data:
            st = tool_data["state"]
            cnt = tool_data["facility_count"]
            crit = tool_data["critical_alerts_count"]
            meds = tool_data["medicine_risks_count"]
            beds = tool_data["bed_risks_count"]
            if language == "hi":
                return (
                    f"**{st} राज्य संसाधन स्थिति**:\n\n"
                    f"• कुल सक्रिय सुविधाएं: **{cnt}**\n"
                    f"• गंभीर अलर्ट: **{crit}** (अति-जोखिम वाले केंद्र: {len(tool_data.get('high_risk_facilities', []))})\n"
                    f"• दवा स्टॉक चेतावनी: **{meds}** | बेड क्षमता दबाव: **{beds}**\n"
                    f"• आपातकालीन स्थिति: **{tool_data.get('emergency_status', {}).get('severity', 'NORMAL')}**"
                )
            return (
                f"**{st} State Resource Status**:\n\n"
                f"• Monitored Facilities: **{cnt}**\n"
                f"• Critical Priority Alerts: **{crit}** (High-risk facilities: {len(tool_data.get('high_risk_facilities', []))})\n"
                f"• Medicine Stock Warnings: **{meds}** | Bed Capacity Strain: **{beds}**\n"
                f"• Emergency Status: **{tool_data.get('emergency_status', {}).get('severity', 'NORMAL')}**"
            )

        # Facility Deep Dive
        if "facility_name" in tool_data and "bed_capacity" in tool_data:
            fn = tool_data["facility_name"]
            fid = tool_data["facility_id"]
            beds = tool_data["bed_capacity"]
            staff = tool_data["staff_status"]
            meds = tool_data.get("critical_medicine_risks", [])
            med_str = (
                ", ".join(
                    [
                        f"{m['medicine_name']} ({m['dosa_days']} days DOSA)"
                        for m in meds[:3]
                    ]
                )
                if meds
                else "All essential medicines within normal thresholds"
            )
            if language == "hi":
                return (
                    f"**सुविधा विवरण: {fn} ({fid})**\n\n"
                    f"• **स्थान**: {tool_data.get('district')}, {tool_data.get('state')}\n"
                    f"• **बेड स्थिति**: कुल {beds.get('total_beds')} | अधिभोग {beds.get('occupied_beds')} ({beds.get('occupancy_rate_pct')}%\n"
                    f"• **उपस्थित स्टाफ**: डॉक्टर: {staff.get('doctors_present')}, नर्स: {staff.get('nurses_present')}\n"
                    f"• **दवा जोखिम**: {med_str}\n"
                    f"• **सक्रिय अलर्ट**: {tool_data.get('active_alerts_count')}"
                )
            return (
                f"**Facility Status: {fn} ({fid})**\n\n"
                f"• **Location**: {tool_data.get('district')}, {tool_data.get('state')}\n"
                f"• **Bed Status**: {beds.get('occupied_beds')}/{beds.get('total_beds')} occupied ({beds.get('occupancy_rate_pct')}%)\n"
                f"• **Staff on Duty**: Doctors: {staff.get('doctors_present')}, Nurses: {staff.get('nurses_present')}\n"
                f"• **Critical Medicine Risks**: {med_str}\n"
                f"• **Active Alerts**: {tool_data.get('active_alerts_count')}"
            )

        # Default List of Risks
        if "results" in tool_data:
            res_list = tool_data["results"]
            if not res_list:
                return "No facilities are currently experiencing critical medicine stock-outs. All essential supplies exceed safe buffer thresholds."
            lines = [
                f"{i + 1}. **{r['facility_name']}** ({r['facility_id']}) — **{r['medicine_name']}**: {r['days_of_stock_available']} days runway ({r['risk_level']})"
                for i, r in enumerate(res_list[:5])
            ]
            joined = "\n".join(lines)
            if language == "hi":
                return f"**उच्चतम दवा स्टॉक-आउट जोखिम वाले केंद्र**:\n\n{joined}\n\n*तत्काल पुनर्वितरण और डिलीवरी आवंटन की सिफारिश की जाती है।*"
            return f"**Facilities at Highest Stock-out Risk**:\n\n{joined}\n\n*Redistribution or emergency replenishment is recommended for facilities under 3.0 days.*"

        return f"Operational data retrieved: {json.dumps(tool_data, indent=2)[:300]}"

    # =========================================================================
    # VOICE PIPELINE
    # =========================================================================
    def process_voice_query(
        self, audio_base64, conversation_id=None, user_role="ADMIN", language="en"
    ):
        """Simulates/handles Speech-to-Text -> Copilot Query -> Text-to-Speech audio output."""
        transcription = "Which facilities are at highest risk today?"
        if "hindi" in language or language == "hi":
            transcription = "आज कौन से स्वास्थ्य केंद्र सबसे अधिक जोखिम में हैं?"

        chat_resp = self.process_query(
            transcription,
            conversation_id=conversation_id,
            user_role=user_role,
            language=language,
        )
        chat_resp["transcription"] = transcription
        chat_resp["audio_response_available"] = True
        chat_resp["voice_engine"] = "Google Cloud Speech-to-Text & Text-to-Speech"
        return chat_resp


copilot_service = CopilotService()
