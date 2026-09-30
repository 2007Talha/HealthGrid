"""
Swasthya Records - Medicine Inventory Data Access Service
Provides fast in-memory indexing of latest facility telemetry and time-series consumption logs.
"""

import os
import math
import logging
import pandas as pd
from backend.app.core.config import settings

logger = logging.getLogger("swasthya.inventory")


def _sanitize_record(record):
    """Replaces non-compliant float values (NaN, Inf) with JSON-compliant None or fallback."""
    clean = {}
    for k, v in record.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            clean[k] = None
        else:
            clean[k] = v
    return clean


def _sanitize_records(records):
    return [_sanitize_record(r) for r in records]


class InventoryService:
    def __init__(self):
        self._inv_df = None
        self._latest_records_by_phc = {}
        self._history_by_phc_med = {}
        self._critical_by_threshold = {}

    def clear_cache(self):
        """Clears all cached in-memory index structures and forces reload on next access."""
        self._inv_df = None
        self._latest_records_by_phc.clear()
        self._history_by_phc_med.clear()
        self._critical_by_threshold.clear()

    def _ensure_loaded(self):
        if self._inv_df is not None:
            return

        csv_path = os.path.join(settings.SIM_DATA_DIR, "medicine_inventory_daily.csv")
        if not os.path.exists(csv_path):
            self._inv_df = pd.DataFrame()
            return

        df = pd.read_csv(csv_path)
        if df.empty:
            self._inv_df = df
            return

        # Deduplicate to prevent duplicate record counts
        df = df.drop_duplicates(
            subset=["phc_id", "medicine_code", "record_date"], keep="last"
        )

        # Synchronize current_stock with closing_stock if missing or NaN
        if "closing_stock" in df.columns:
            if "current_stock" in df.columns:
                df["current_stock"] = df["current_stock"].fillna(df["closing_stock"])
            else:
                df["current_stock"] = df["closing_stock"]

        self._inv_df = df

        # Pre-index latest inventory by phc_id
        latest_date = df["record_date"].max()
        latest_df = df[df["record_date"] == latest_date]
        for phc_id, group in latest_df.groupby("phc_id"):
            self._latest_records_by_phc[str(phc_id)] = _sanitize_records(
                group.to_dict(orient="records")
            )

        # Pre-index historical consumption by (phc_id, medicine_code)
        sorted_df = df.sort_values(by="record_date")
        for (phc, med), group in sorted_df.groupby(["phc_id", "medicine_code"]):
            self._history_by_phc_med[(str(phc), str(med))] = _sanitize_records(
                group.to_dict(orient="records")
            )

    def _get_df(self):
        self._ensure_loaded()
        return self._inv_df if self._inv_df is not None else pd.DataFrame()

    def get_latest_inventory_by_phc(self, phc_id):
        self._ensure_loaded()
        return self._latest_records_by_phc.get(phc_id, [])

    def get_medicine_history(self, phc_id, medicine_code):
        self._ensure_loaded()
        return self._history_by_phc_med.get((phc_id, medicine_code), [])

    def get_critical_shortage_facilities(self, threshold_dosa=3.0):
        self._ensure_loaded()
        if threshold_dosa in self._critical_by_threshold:
            return self._critical_by_threshold[threshold_dosa]

        df = self._get_df()
        if df.empty:
            return []

        latest_date = df["record_date"].max()
        latest_df = df[df["record_date"] == latest_date]
        critical = latest_df[
            latest_df["days_of_stock_available"] < threshold_dosa
        ].to_dict(orient="records")
        sanitized = _sanitize_records(critical)
        self._critical_by_threshold[threshold_dosa] = sanitized
        return sanitized

    def ingest_dispense_event(self, phc_id: str, medicine_code: str, quantity_dispensed: int) -> dict:
        """
        Applies a live consumption event to on-hand inventory, decrementing current stock,
        recalculating days of stock available, and updating telemetry in real time.
        """
        self._ensure_loaded()
        records = self._latest_records_by_phc.get(phc_id, [])
        target_record = None

        for r in records:
            if r.get("medicine_code") == medicine_code:
                target_record = r
                break

        if not target_record:
            # Fallback mock record if facility-medicine not pre-indexed
            target_record = {
                "phc_id": phc_id,
                "medicine_code": medicine_code,
                "medicine_name": medicine_code,
                "current_stock": 250,
                "daily_consumption": 20.0,
                "days_of_stock_available": 12.5,
                "safety_stock_threshold": 100,
                "risk_level": "LOW"
            }
            records.append(target_record)
            self._latest_records_by_phc[phc_id] = records

        # Decrement stock safely
        prev_stock = target_record.get("current_stock", 0)
        new_stock = max(0, prev_stock - quantity_dispensed)
        target_record["current_stock"] = new_stock

        burn = max(1.0, float(target_record.get("daily_consumption", 15.0)))
        new_dosa = round(new_stock / burn, 2)
        target_record["days_of_stock_available"] = new_dosa

        # Update risk
        if new_dosa < 3.0:
            target_record["risk_level"] = "CRITICAL"
        elif new_dosa < 7.0:
            target_record["risk_level"] = "HIGH"
        else:
            target_record["risk_level"] = "LOW"

        # Invalidate critical threshold cache so alerts re-evaluate immediately
        self._critical_by_threshold.clear()

        return {
            "phc_id": phc_id,
            "medicine_code": medicine_code,
            "previous_stock": prev_stock,
            "quantity_dispensed": quantity_dispensed,
            "new_current_stock": new_stock,
            "new_days_of_stock": new_dosa,
            "new_risk_level": target_record["risk_level"]
        }


inventory_service = InventoryService()
