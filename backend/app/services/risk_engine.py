"""
Swasthya Records - Stock-Out Risk & Inventory Coverage Evaluation Engine
Calculates Days of Stock Available (DOSA), exact projected stock-out dates,
safety-stock thresholds, and multi-tier hazard risk scores.
"""

import os
import math
import time
import threading
import datetime
import pandas as pd
import numpy as np

from backend.app.core.config import settings
from backend.app.services.ml_forecasting import forecasting_engine
from backend.app.services.delivery_service import delivery_service
from backend.app.services.anomaly_detector import anomaly_detector


class StockRiskEngine:
    def __init__(self):
        self._cached_all_risks = None
        self._cache_timestamp = 0.0
        self._eval_lock = threading.Lock()

    def evaluate_medicine_stock_risk(self, phc_id, medicine_code):
        """Evaluates detailed stock-out risk, projected exhaustion date, and safety thresholds for a specific medicine."""
        from backend.app.services.inventory_service import inventory_service

        # 1. Fetch current stock & metadata
        phc_inventory = inventory_service.get_latest_inventory_by_phc(phc_id)
        med_records = [r for r in phc_inventory if r["medicine_code"] == medicine_code]
        if not med_records:
            return {
                "phc_id": phc_id,
                "medicine_code": medicine_code,
                "risk_level": "UNKNOWN",
                "evidence_summary": "Insufficient data to determine this reliably.",
            }

        current_record = med_records[0]
        current_stock = int(
            current_record.get("closing_stock", current_record.get("current_stock", 0))
        )
        med_name = current_record["medicine_name"]
        cat = current_record["therapeutic_category"]
        facility_name = current_record["facility_name"]

        # 2. Fetch ML multi-day demand forecast (14 days)
        forecasts = forecasting_engine.forecast_medicine_demand(
            phc_id, medicine_code, horizon_days=14
        )
        if not forecasts:
            return {
                "phc_id": phc_id,
                "medicine_code": medicine_code,
                "risk_level": "UNKNOWN",
                "evidence_summary": "Insufficient data to determine this reliably.",
            }

        # 3. Fetch in-transit deliveries scheduled for this facility & medicine
        in_transit = delivery_service.get_in_transit_deliveries(phc_id)
        scheduled_deliveries = [
            d for d in in_transit if d["medicine_code"] == medicine_code
        ]

        # 4. Day-by-day projected inventory trajectory
        sim_stock = current_stock
        stockout_date = None
        stockout_horizon_days = None
        projected_curve = []

        for f in forecasts:
            target_date_str = f["target_date"]
            daily_demand = f["predicted_consumption"]

            # Add scheduled incoming deliveries on arrival day
            incoming_qty = sum(
                d["quantity"]
                for d in scheduled_deliveries
                if str(d.get("expected_arrival_date")) == target_date_str
            )

            sim_stock = sim_stock + incoming_qty - daily_demand
            projected_curve.append(
                {
                    "date": target_date_str,
                    "predicted_consumption": daily_demand,
                    "incoming_deliveries": incoming_qty,
                    "projected_closing_stock": max(0.0, round(sim_stock, 1)),
                }
            )

            if sim_stock <= 0 and stockout_date is None:
                stockout_date = target_date_str
                stockout_horizon_days = f["horizon_day"]

        # 5. DOSA and Safety Stock Calculation
        avg_7d_burn = max(
            1.0, float(np.mean([f["predicted_consumption"] for f in forecasts[:7]]))
        )
        dosa = round(current_stock / avg_7d_burn, 2)

        demand_std = float(np.std([f["predicted_consumption"] for f in forecasts[:7]]))
        lead_time_days = 5
        # Standard safety stock: Z * sigma_d * sqrt(L) + 3-day buffer
        safety_stock_threshold = int(
            round(1.65 * demand_std * math.sqrt(lead_time_days) + 3.0 * avg_7d_burn)
        )

        # 6. Risk Level Classification
        if (
            current_stock == 0
            or (stockout_horizon_days is not None and stockout_horizon_days <= 2.0)
            or dosa < 2.0
        ):
            risk_level = "CRITICAL"
        elif (
            stockout_horizon_days is not None and stockout_horizon_days <= 5.0
        ) or dosa < 5.0:
            risk_level = "HIGH"
        elif current_stock < safety_stock_threshold or dosa < 10.0:
            risk_level = "WARNING"
        else:
            risk_level = "LOW"

        # 7. Check Anomaly
        history = inventory_service.get_medicine_history(phc_id, medicine_code)
        past_consumptions = [h["daily_consumption"] for h in history[-14:]]
        anomaly_info = anomaly_detector.detect_consumption_anomalies(
            past_consumptions, float(current_record["daily_consumption"])
        )

        # Evidence Summary String
        if stockout_date:
            stockout_str = f"Projected stock-out in ~{stockout_horizon_days} days ({stockout_date})."
        else:
            stockout_str = f"Adequate stock coverage for >14 days (DOSA: {dosa} days)."

        evidence = (
            f"Current Physical Stock: {current_stock:,} units | "
            f"Predicted 7-Day Burn Rate: {avg_7d_burn:.1f} units/day | "
            f"Safety Stock Threshold: {safety_stock_threshold:,} units | "
            f"DOSA: {dosa:.1f} days | {stockout_str}"
        )
        if anomaly_info["is_anomaly"]:
            evidence += f" (Note: Demand is {anomaly_info['percentage_deviation']}% above baseline z-score {anomaly_info['z_score']})."

        return {
            "phc_id": phc_id,
            "facility_name": facility_name,
            "medicine_code": medicine_code,
            "medicine_name": med_name,
            "therapeutic_category": cat,
            "current_stock": current_stock,
            "average_daily_predicted_demand": round(avg_7d_burn, 1),
            "days_of_stock_available": dosa,
            "safety_stock_threshold": safety_stock_threshold,
            "risk_level": risk_level,
            "projected_stockout_date": stockout_date,
            "projected_stockout_horizon_days": stockout_horizon_days,
            "anomaly_detected": anomaly_info["is_anomaly"],
            "anomaly_percentage_deviation": anomaly_info["percentage_deviation"],
            "evidence_summary": evidence,
            "projected_trajectory": projected_curve,
            "model_version": forecasts[0]["model_version"],
            "evaluated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

    def clear_cache(self):
        with self._eval_lock:
            self._cached_all_risks = None
            self._cache_timestamp = 0.0

    def evaluate_all_facility_risks(self):
        """Evaluates stock-out risks across all 33 facilities and 20 medicines with fast in-memory caching."""
        now = time.time()
        if self._cached_all_risks is not None and (now - self._cache_timestamp) < 300.0:
            return self._cached_all_risks

        with self._eval_lock:
            # Double-check inside lock
            if (
                self._cached_all_risks is not None
                and (now - self._cache_timestamp) < 300.0
            ):
                return self._cached_all_risks

            # Fast load precomputed evaluations if available
            csv_path = os.path.join(
                settings.DATA_DIR,
                "processed",
                "forecasts",
                "stock_risk_evaluations.csv",
            )
            if os.path.exists(csv_path):
                try:
                    df = pd.read_csv(csv_path)
                    # Hydrate missing helper fields
                    records = df.to_dict(orient="records")
                    for r in records:
                        if "projected_stockout_horizon_days" not in r or pd.isna(
                            r.get("projected_stockout_horizon_days")
                        ):
                            dosa = float(r.get("days_of_stock_available", 99.0))
                            r["projected_stockout_horizon_days"] = (
                                dosa if dosa <= 14.0 else None
                            )
                        if "projected_trajectory" not in r or not isinstance(
                            r.get("projected_trajectory"), list
                        ):
                            r["projected_trajectory"] = []
                    self._cached_all_risks = records
                    self._cache_timestamp = now
                    return self._cached_all_risks
                except Exception:
                    pass

            from backend.app.services.inventory_service import inventory_service

            inv_df = inventory_service._get_df()
            if inv_df.empty:
                return []

            latest_date = inv_df["record_date"].max()
            latest_records = inv_df[inv_df["record_date"] == latest_date]

            all_risks = []
            for _, row in latest_records.iterrows():
                risk_eval = self.evaluate_medicine_stock_risk(
                    row["phc_id"], row["medicine_code"]
                )
                all_risks.append(risk_eval)

            self._cached_all_risks = all_risks
            self._cache_timestamp = now
            return all_risks

    evaluate_facility_medicine_risk = evaluate_medicine_stock_risk


risk_engine = StockRiskEngine()
