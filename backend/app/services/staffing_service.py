"""
Swasthya Records - Medical Staffing & Attendance Service
"""

import os
import pandas as pd
from backend.app.core.config import settings


class StaffingService:
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

    def get_latest_staffing_status(self, phc_id=None):
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
            "doctors_scheduled",
            "doctors_present",
            "nurses_scheduled",
            "nurses_present",
            "doctor_shortage_flag",
            "nurse_shortage_flag",
        ]
        return latest_df[cols].to_dict(orient="records")


staffing_service = StaffingService()
