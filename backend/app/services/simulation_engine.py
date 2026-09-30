"""
Swasthya Records - High-Fidelity PHC Operational Telemetry Simulator
Stochastically simulates realistic daily time-series operational feeds:
- Patient Footfall (OPD, IPD, Fever syndromic surveillance)
- Bed Occupancy & Availability
- Medical Staff Attendance & Shortages
- Medicine Inventory, Consumption, Stock-outs, and Deliveries
- Dynamic Emergency Scenario Multipliers
All generated records carry data_source = "SIMULATED".
"""

import os
import math
import random
import uuid
import logging
import datetime
import pandas as pd
import numpy as np

from backend.app.core.config import settings

logger = logging.getLogger("swasthya.simulator")

# Set deterministic seed for reproducible baseline with realistic variance
RANDOM_SEED = 42


class SimulationEngine:
    def __init__(self):
        self.facilities_df = pd.DataFrame()
        self.medicines_df = pd.DataFrame()
        self.active_emergencies = {}
        self.current_sim_date = datetime.date(2026, 8, 23)
        self.inventory_state = {}  # (phc_id, med_code) -> current_stock
        self.active_deliveries = []
        self.facility_daily_logs = []
        self.inventory_daily_logs = []
        self.delivery_logs = []

        self._load_master_data()

    def _load_master_data(self):
        fac_path = os.path.join(settings.GOV_DATA_DIR, "clean_facility_master.csv")
        med_path = os.path.join(settings.GOV_DATA_DIR, "clean_medicine_reference.csv")

        if os.path.exists(fac_path) and os.path.exists(med_path):
            self.facilities_df = pd.read_csv(fac_path)
            self.medicines_df = pd.read_csv(med_path)
        else:
            raise FileNotFoundError(
                "Cleaned government master datasets not found. Run Phase 1 ingestion first."
            )

        # Load existing operational simulation history if present
        fac_out = os.path.join(settings.SIM_DATA_DIR, "phc_operational_daily.csv")
        inv_out = os.path.join(settings.SIM_DATA_DIR, "medicine_inventory_daily.csv")
        del_out = os.path.join(settings.SIM_DATA_DIR, "medicine_deliveries.csv")
        if os.path.exists(fac_out) and os.path.exists(inv_out):
            try:
                self.facility_daily_logs = pd.read_csv(fac_out).to_dict(
                    orient="records"
                )
                self.inventory_daily_logs = pd.read_csv(inv_out).to_dict(
                    orient="records"
                )
                if os.path.exists(del_out):
                    self.delivery_logs = pd.read_csv(del_out).to_dict(orient="records")
                if self.inventory_daily_logs:
                    latest_date = max(
                        r["record_date"] for r in self.inventory_daily_logs
                    )
                    for r in self.inventory_daily_logs:
                        if r["record_date"] == latest_date:
                            self.inventory_state[(r["phc_id"], r["medicine_code"])] = (
                                int(r["closing_stock"])
                            )
            except Exception:
                pass

    def _get_medicine_consumption_rate(self, med_code, facility_type):
        """Returns standard baseline units consumed per 100 total patient footfall."""
        rates = {
            "MED-PCM-500": 45.0,  # Paracetamol 500mg
            "MED-PCM-SYR": 18.0,  # Paracetamol Syrup
            "MED-AMX-500": 22.0,  # Amoxicillin 500mg
            "MED-AMC-625": 14.0,  # Amoxicillin + Clav
            "MED-ORS-SFT": 32.0,  # ORS Sachet
            "MED-ZNC-20": 16.0,  # Zinc Sulfate
            "MED-AZI-500": 12.0,  # Azithromycin 500mg
            "MED-CTX-1G": 6.0,  # Ceftriaxone Injection
            "MED-RAB-VAC": 3.5,  # Anti-Rabies Vaccine
            "MED-ASV-VIAL": 1.2,  # Anti-Snake Venom Serum
            "MED-INS-REG": 4.0,  # Human Insulin
            "MED-MET-500": 25.0,  # Metformin 500mg
            "MED-OXY-AMP": 5.0,  # Oxytocin Injection
            "MED-MGS-50": 2.5,  # Magnesium Sulfate
            "MED-IVF-NS500": 15.0,  # Normal Saline 500ml
            "MED-IVF-RL500": 12.0,  # Ringer's Lactate
            "MED-IVF-D5500": 8.0,  # Dextrose 5%
            "MED-ART-60": 3.0,  # Artesunate Injection
            "MED-ALB-400": 8.0,  # Albendazole
            "MED-IFA-TAB": 28.0,  # Iron & Folic Acid
        }
        base_rate = rates.get(med_code, 10.0)
        if facility_type == "District Hospital":
            base_rate *= 1.35
        elif facility_type == "CHC":
            base_rate *= 1.15
        return base_rate

    def _get_active_emergency_multiplier(self, district_code, med_code=None):
        """Calculates combined demand multiplier from all active emergency events."""
        multiplier = 1.0
        for scen_id, scen in self.active_emergencies.items():
            if district_code in scen["affected_district_ids"]:
                # Check medicine-specific outbreak dynamics
                scen_type = scen["event_type"]
                scen_mult = scen["demand_multiplier"]

                if scen_type == "DISEASE_OUTBREAK" or scen_type == "PATIENT_SURGE":
                    if med_code in [
                        "MED-PCM-500",
                        "MED-PCM-SYR",
                        "MED-AMX-500",
                        "MED-ORS-SFT",
                        "MED-IVF-NS500",
                        "MED-CTX-1G",
                    ]:
                        multiplier *= scen_mult * 1.25
                    else:
                        multiplier *= scen_mult
                elif scen_type == "FLOOD":
                    if med_code in [
                        "MED-ORS-SFT",
                        "MED-ZNC-20",
                        "MED-IVF-RL500",
                        "MED-ASV-VIAL",
                        "MED-AMX-500",
                    ]:
                        multiplier *= scen_mult * 1.40
                    else:
                        multiplier *= scen_mult
                elif scen_type == "HEATWAVE":
                    if med_code in [
                        "MED-ORS-SFT",
                        "MED-IVF-NS500",
                        "MED-IVF-RL500",
                        "MED-PCM-500",
                    ]:
                        multiplier *= scen_mult * 1.35
                    else:
                        multiplier *= scen_mult
                else:
                    multiplier *= scen_mult
        return min(multiplier, 5.0)

    def initialize_inventory(self):
        """Initializes starting inventory for all PHCs across 20 medicines."""
        random.seed(RANDOM_SEED)
        np.random.seed(RANDOM_SEED)
        self.inventory_state.clear()

        for _, fac in self.facilities_df.iterrows():
            phc_id = fac["facility_id"]
            fac_type = fac["facility_type"]
            pop = fac["catchment_population"]

            # Base footfall estimation
            if fac_type == "District Hospital":
                base_ff = max(800, int(pop * 0.0018))
            elif fac_type == "CHC":
                base_ff = max(250, int(pop * 0.0014))
            else:  # PHC
                base_ff = max(70, int(pop * 0.0010))

            for _, med in self.medicines_df.iterrows():
                med_code = med["medicine_code"]
                cons_rate = self._get_medicine_consumption_rate(med_code, fac_type)
                avg_daily_burn = max(2, int((base_ff / 100.0) * cons_rate))

                # Starting buffer between 15 and 28 days of stock
                stock_days = random.uniform(15.0, 28.0)

                # Special scenario injection for hackathon demo:
                # Set PHC Bakhtiyarpur (PHC-BR-PAT-001) to have a low initial buffer for Paracetamol & ORS
                if phc_id == "PHC-BR-PAT-001" and med_code in [
                    "MED-PCM-500",
                    "MED-ORS-SFT",
                ]:
                    stock_days = 4.2  # Will quickly drop to critical during surge
                # Set PHC Danapur (PHC-BR-PAT-002) to have high surplus
                elif phc_id == "PHC-BR-PAT-002" and med_code in [
                    "MED-PCM-500",
                    "MED-ORS-SFT",
                ]:
                    stock_days = 32.0  # Ample surplus for redistribution

                initial_stock = int(avg_daily_burn * stock_days)
                self.inventory_state[(phc_id, med_code)] = initial_stock

    def simulate_day(self, current_date):
        """Simulates all facility and inventory operational logs for a single 24-hour day."""
        day_fac_logs = []
        day_inv_logs = []

        weekday = current_date.weekday()  # 0 = Monday, 6 = Sunday
        # Day of week multiplier
        if weekday == 0:
            dow_mult = 1.32  # Monday post-weekend surge
        elif weekday in [1, 2, 3]:
            dow_mult = 1.05  # Midweek normal
        elif weekday in [4, 5]:
            dow_mult = 0.90  # Weekend decline
        else:
            dow_mult = 0.38  # Sunday minimal OPD / emergency only

        # Seasonal disease wave factor
        # Simulating monsoon surge in July/August (Days 30-70)
        day_of_year = current_date.timetuple().tm_yday
        seasonal_wave = 1.0 + 0.25 * math.sin(2 * math.pi * (day_of_year - 150) / 365.0)

        # Process deliveries arriving today
        for delivery in self.active_deliveries:
            if (
                delivery["status"] == "IN_TRANSIT"
                and delivery["expected_arrival_date"] <= current_date
            ):
                delivery["status"] = "DELIVERED"
                delivery["actual_arrival_date"] = current_date
                key = (delivery["phc_id"], delivery["medicine_code"])
                self.inventory_state[key] = (
                    self.inventory_state.get(key, 0) + delivery["quantity"]
                )

        # Iterate over each facility
        for _, fac in self.facilities_df.iterrows():
            phc_id = fac["facility_id"]
            fac_name = fac["facility_name"]
            fac_type = fac["facility_type"]
            state_name = fac["state_name"]
            district_name = fac["district_name"]
            district_code = fac["district_code"]
            pop = fac["catchment_population"]
            sanctioned_beds = int(fac["sanctioned_beds"])
            sanctioned_docs = int(fac["sanctioned_doctors"])
            sanctioned_nurses = int(fac["sanctioned_nurses"])

            # Base patient footfall calculation
            if fac_type == "District Hospital":
                base_footfall = pop * 0.0018
            elif fac_type == "CHC":
                base_footfall = pop * 0.0014
            else:
                base_footfall = pop * 0.0010

            em_mult = self._get_active_emergency_multiplier(district_code)
            stochastic_noise = np.random.normal(1.0, 0.06)

            actual_footfall = max(
                15,
                int(
                    base_footfall
                    * dow_mult
                    * seasonal_wave
                    * em_mult
                    * stochastic_noise
                ),
            )
            opd_patients = int(actual_footfall * random.uniform(0.86, 0.92))
            ipd_patients = actual_footfall - opd_patients
            fever_cases = int(
                actual_footfall
                * random.uniform(0.08, 0.22)
                * (1.5 if em_mult > 1.1 else 1.0)
            )

            # Bed occupancy dynamics
            avg_stay_factor = 2.4
            raw_occupied = int(
                ipd_patients * avg_stay_factor * random.uniform(0.85, 1.15)
            )
            beds_occupied = min(sanctioned_beds, max(0, raw_occupied))
            beds_available = sanctioned_beds - beds_occupied
            bed_occ_rate = round(
                (beds_occupied / sanctioned_beds * 100.0)
                if sanctioned_beds > 0
                else 0.0,
                2,
            )

            # Staff attendance dynamics
            # Ensure doctors_present <= doctors_scheduled and nurses_present <= nurses_scheduled
            doc_att_rate = (
                random.uniform(0.80, 1.0)
                if weekday != 6
                else random.uniform(0.50, 0.70)
            )
            nurse_att_rate = (
                random.uniform(0.85, 1.0)
                if weekday != 6
                else random.uniform(0.60, 0.80)
            )

            docs_present = min(
                sanctioned_docs, max(1, int(math.ceil(sanctioned_docs * doc_att_rate)))
            )
            nurses_present = min(
                sanctioned_nurses,
                max(1, int(math.ceil(sanctioned_nurses * nurse_att_rate))),
            )

            doc_shortage = (docs_present < sanctioned_docs) and (em_mult > 1.2)
            nurse_shortage = nurses_present < math.ceil(sanctioned_nurses * 0.7)

            # Emergency status tag
            if em_mult >= 1.5:
                em_status = "CRITICAL_SURGE"
            elif em_mult > 1.1:
                em_status = "SURGE_ALERT"
            elif beds_occupied >= sanctioned_beds:
                em_status = "BED_OVERFLOW"
            else:
                em_status = "NORMAL"

            fac_log = {
                "phc_id": phc_id,
                "facility_name": fac_name,
                "state_name": state_name,
                "district_name": district_name,
                "district_code": district_code,
                "record_date": current_date.isoformat(),
                "timestamp": datetime.datetime.combine(
                    current_date, datetime.time(20, 0, 0)
                ).isoformat(),
                "patient_footfall": actual_footfall,
                "opd_patients": opd_patients,
                "ipd_patients": ipd_patients,
                "fever_syndromic_cases": fever_cases,
                "beds_total": sanctioned_beds,
                "beds_occupied": beds_occupied,
                "beds_available": beds_available,
                "bed_occupancy_rate_pct": bed_occ_rate,
                "doctors_scheduled": sanctioned_docs,
                "doctors_present": docs_present,
                "nurses_scheduled": sanctioned_nurses,
                "nurses_present": nurses_present,
                "doctor_shortage_flag": doc_shortage,
                "nurse_shortage_flag": nurse_shortage,
                "emergency_status": em_status,
                "data_source": "SIMULATED",
            }
            day_fac_logs.append(fac_log)

            # Medicine inventory simulation for this facility
            for _, med in self.medicines_df.iterrows():
                med_code = med["medicine_code"]
                med_name = med["medicine_name"]
                cat = med["therapeutic_category"]

                key = (phc_id, med_code)
                opening_stock = self.inventory_state.get(key, 100)

                # Consumption calculation
                cons_rate = self._get_medicine_consumption_rate(med_code, fac_type)
                med_em_mult = self._get_active_emergency_multiplier(
                    district_code, med_code
                )
                cons_noise = np.random.normal(1.0, 0.08)

                expected_consumption = (
                    (actual_footfall / 100.0)
                    * cons_rate
                    * (med_em_mult / em_mult if em_mult > 0 else 1.0)
                    * cons_noise
                )
                daily_consumption = max(1, int(round(expected_consumption)))

                # Check for deliveries received today for this specific medicine
                received_qty = 0
                for d in self.active_deliveries:
                    if (
                        d["phc_id"] == phc_id
                        and d["medicine_code"] == med_code
                        and d["status"] == "DELIVERED"
                        and d["actual_arrival_date"] == current_date
                    ):
                        received_qty += d["quantity"]

                # Strict inventory balance conservation:
                # closing_stock = max(0, opening_stock + received_quantity - daily_consumption)
                raw_closing = opening_stock + received_qty - daily_consumption
                if raw_closing <= 0:
                    closing_stock = 0
                    stock_out = True
                else:
                    closing_stock = raw_closing
                    stock_out = False

                self.inventory_state[key] = closing_stock

                # Safety and reorder calculations
                avg_daily_burn = max(2, int((base_footfall / 100.0) * cons_rate))
                reorder_level = avg_daily_burn * 7
                safety_stock = avg_daily_burn * 3
                dosa = round(closing_stock / max(1.0, float(daily_consumption)), 2)

                # Check if we should trigger an automated replenishment delivery
                has_pending_delivery = any(
                    d["phc_id"] == phc_id
                    and d["medicine_code"] == med_code
                    and d["status"] in ["SCHEDULED", "IN_TRANSIT"]
                    for d in self.active_deliveries
                )

                if closing_stock <= reorder_level and not has_pending_delivery:
                    lead_time = random.randint(4, 7)
                    order_qty = avg_daily_burn * 14  # 2-week restock
                    new_delivery = {
                        "delivery_id": f"DEL-{uuid.uuid4().hex[:8].upper()}",
                        "phc_id": phc_id,
                        "facility_name": fac_name,
                        "medicine_code": med_code,
                        "medicine_name": med_name,
                        "quantity": order_qty,
                        "dispatch_date": current_date,
                        "expected_arrival_date": current_date
                        + datetime.timedelta(days=lead_time),
                        "actual_arrival_date": None,
                        "status": "IN_TRANSIT",
                        "data_source": "SIMULATED",
                    }
                    self.active_deliveries.append(new_delivery)
                    self.delivery_logs.append(new_delivery)

                inv_log = {
                    "phc_id": phc_id,
                    "facility_name": fac_name,
                    "medicine_code": med_code,
                    "medicine_name": med_name,
                    "therapeutic_category": cat,
                    "record_date": current_date.isoformat(),
                    "opening_stock": opening_stock,
                    "received_quantity": received_qty,
                    "daily_consumption": daily_consumption,
                    "closing_stock": closing_stock,
                    "reorder_level": reorder_level,
                    "safety_stock": safety_stock,
                    "days_of_stock_available": dosa,
                    "stock_out_occurred": stock_out,
                    "data_source": "SIMULATED",
                }
                day_inv_logs.append(inv_log)

        return day_fac_logs, day_inv_logs

    def generate_historical_timeseries(self, days=90):
        """Generates 90 days of synthetic historical operational logs."""
        logger.info(
            "Initializing %d-day historical operational time-series for %d facilities...",
            days,
            len(self.facilities_df),
        )
        self.initialize_inventory()
        self.facility_daily_logs.clear()
        self.inventory_daily_logs.clear()
        self.delivery_logs.clear()

        start_date = self.current_sim_date - datetime.timedelta(days=days)

        # Inject controlled historical event: Dengue outbreak in Patna District around day 60-75
        self.active_emergencies["SCEN-HIST-DENGUE-PATNA"] = {
            "scenario_id": "SCEN-HIST-DENGUE-PATNA",
            "event_type": "DISEASE_OUTBREAK",
            "affected_district_ids": ["BR-PATNA"],
            "demand_multiplier": 1.45,
            "severity": "HIGH",
            "duration_days": 15,
            "start_day": 55,
            "end_day": 70,
        }

        for day_idx in range(days):
            sim_date = start_date + datetime.timedelta(days=day_idx)

            # Manage emergency scenario activation window
            if day_idx < 55 or day_idx > 70:
                self.active_emergencies.pop("SCEN-HIST-DENGUE-PATNA", None)
            else:
                self.active_emergencies["SCEN-HIST-DENGUE-PATNA"] = {
                    "scenario_id": "SCEN-HIST-DENGUE-PATNA",
                    "event_type": "DISEASE_OUTBREAK",
                    "affected_district_ids": ["BR-PATNA"],
                    "demand_multiplier": 1.45,
                    "severity": "HIGH",
                    "duration_days": 15,
                }

            f_logs, i_logs = self.simulate_day(sim_date)
            self.facility_daily_logs.extend(f_logs)
            self.inventory_daily_logs.extend(i_logs)

        logger.info(
            "Simulation complete — Generated %d facility records and %d inventory records.",
            len(self.facility_daily_logs),
            len(self.inventory_daily_logs),
        )
        self.export_processed_data()

        return {
            "total_facility_days": len(self.facility_daily_logs),
            "total_inventory_records": len(self.inventory_daily_logs),
            "total_deliveries_logged": len(self.delivery_logs),
            "simulated_date_range": f"{start_date.isoformat()} to {self.current_sim_date.isoformat()}",
        }

    def export_processed_data(self):
        """Exports the generated operational datasets to CSV in data/processed/simulated/."""
        os.makedirs(settings.SIM_DATA_DIR, exist_ok=True)

        fac_df = pd.DataFrame(self.facility_daily_logs)
        inv_df = pd.DataFrame(self.inventory_daily_logs)
        del_df = pd.DataFrame(self.delivery_logs)

        fac_out = os.path.join(settings.SIM_DATA_DIR, "phc_operational_daily.csv")
        inv_out = os.path.join(settings.SIM_DATA_DIR, "medicine_inventory_daily.csv")
        del_out = os.path.join(settings.SIM_DATA_DIR, "medicine_deliveries.csv")

        fac_df.to_csv(fac_out, index=False)
        inv_df.to_csv(inv_out, index=False)
        del_df.to_csv(del_out, index=False)

        try:
            from backend.app.services.inventory_service import inventory_service

            inventory_service._inv_df = None
        except Exception:
            pass

        logger.info(
            "Export complete — %s (%d rows), %s (%d rows), %s (%d rows)",
            fac_out,
            len(fac_df),
            inv_out,
            len(inv_df),
            del_out,
            len(del_df),
        )

    def trigger_emergency(self, scenario_req):
        """Injects a real-time emergency scenario multiplier into target districts."""
        scenario_id = f"SCEN-{uuid.uuid4().hex[:8].upper()}"
        scenario_data = {
            "scenario_id": scenario_id,
            "event_type": scenario_req["event_type"],
            "affected_district_ids": scenario_req["affected_district_ids"],
            "demand_multiplier": float(scenario_req.get("demand_multiplier", 1.40)),
            "severity": scenario_req.get("severity", "HIGH"),
            "duration_days": int(scenario_req.get("duration_days", 7)),
            "status": "ACTIVE",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        self.active_emergencies[scenario_id] = scenario_data

        # Count impacted facilities
        impacted = self.facilities_df[
            self.facilities_df["district_code"].isin(
                scenario_data["affected_district_ids"]
            )
        ]
        scenario_data["facilities_impacted_count"] = len(impacted)
        return scenario_data

    def clear_emergency(self, scenario_id=None):
        """Clears an active emergency scenario or all scenarios."""
        if scenario_id and scenario_id in self.active_emergencies:
            del self.active_emergencies[scenario_id]
        else:
            self.active_emergencies.clear()


# Global Singleton Simulation Instance
simulation_engine = SimulationEngine()
