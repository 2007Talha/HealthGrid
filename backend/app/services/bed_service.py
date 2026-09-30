"""
Swasthya Records - Bed Occupancy Service
"""

import os
import pandas as pd
from backend.app.core.config import settings


class BedService:
    def __init__(self):
        self._fac_df = None

    def _get_df(self):
        if self._fac_df is None:
            csv_path = os.path.join(settings.SIM_DATA_DIR, "phc_operational_daily.csv")
            if os.path.exists(csv_path):
                self._fac_df = pd.read_csv(csv_path)
            else:
                return pd.DataFrame()
        return self._fac_df

    def get_latest_bed_status(self, phc_id=None):
        df = self._get_df()
        if df.empty:
            return []
        latest_date = df["record_date"].max()
        latest_df = df[df["record_date"] == latest_date]
        if phc_id:
            latest_df = latest_df[latest_df["phc_id"] == phc_id]
        cols = [
            "phc_id",
            "facility_name",
            "state_name",
            "district_name",
            "record_date",
            "beds_total",
            "beds_occupied",
            "beds_available",
            "bed_occupancy_rate_pct",
            "emergency_status",
        ]
        records = latest_df[cols].to_dict(orient="records")
        for r in records:
            r["total_beds"] = r.get("beds_total", 0)
            r["occupied_beds"] = r.get("beds_occupied", 0)
            r["available_beds"] = r.get("beds_available", 0)
            r["occupancy_rate_pct"] = r.get("bed_occupancy_rate_pct", 0.0)
        return records

    def get_bed_history(self, phc_id=None, days=14):
        df = self._get_df()
        if df.empty:
            return []
        if phc_id:
            df = df[df["phc_id"] == phc_id]

        # Get unique last N dates
        unique_dates = sorted(df["record_date"].unique())[-days:]
        subset = df[df["record_date"].isin(unique_dates)]

        # Group by record_date to compute daily aggregates
        grouped = (
            subset.groupby("record_date")
            .agg({"beds_total": "sum", "beds_occupied": "sum", "beds_available": "sum"})
            .reset_index()
            .sort_values(by="record_date")
        )

        history = []
        for _, row in grouped.iterrows():
            total = int(row["beds_total"])
            occ = int(row["beds_occupied"])
            avail = int(row["beds_available"])
            pct = round((occ / max(1, total)) * 100.0, 1)
            history.append(
                {
                    "record_date": str(row["record_date"]),
                    "beds_total": total,
                    "total_beds": total,
                    "beds_occupied": occ,
                    "occupied_beds": occ,
                    "beds_available": avail,
                    "available_beds": avail,
                    "bed_occupancy_rate_pct": pct,
                    "occupancy_rate_pct": pct,
                }
            )
        return history

    def get_bed_overflow_alerts(self, threshold_pct=90.0):
        df = self._get_df()
        if df.empty:
            return []
        latest_date = df["record_date"].max()
        latest_df = df[df["record_date"] == latest_date]
        overflow = latest_df[latest_df["bed_occupancy_rate_pct"] >= threshold_pct]
        records = overflow.to_dict(orient="records")
        for r in records:
            r["total_beds"] = r.get("beds_total", 0)
            r["occupied_beds"] = r.get("beds_occupied", 0)
            r["occupancy_rate_pct"] = r.get("bed_occupancy_rate_pct", 0.0)
        return records


bed_service = BedService()
