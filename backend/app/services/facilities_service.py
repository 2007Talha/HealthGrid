"""
Swasthya Records - Facilities Data Service
"""

import os
import pandas as pd
from backend.app.core.config import settings


class FacilitiesService:
    def __init__(self):
        self._df = None

    def _get_df(self):
        if self._df is None:
            path = os.path.join(settings.GOV_DATA_DIR, "clean_facility_master.csv")
            if os.path.exists(path):
                self._df = pd.read_csv(path)
            else:
                self._df = pd.DataFrame()
        return self._df

    def get_all_facilities(self):
        df = self._get_df()
        if df.empty:
            return []
        return df.to_dict(orient="records")

    def get_facility_by_id(self, facility_id):
        df = self._get_df()
        if df.empty:
            return None
        match = df[df["facility_id"] == facility_id]
        if match.empty:
            return None
        return match.iloc[0].to_dict()

    def get_facilities_by_state(self, state_code):
        df = self._get_df()
        if df.empty:
            return []
        return df[df["state_code"] == state_code].to_dict(orient="records")

    def get_facilities_by_district(self, district_code):
        df = self._get_df()
        if df.empty:
            return []
        return df[df["district_code"] == district_code].to_dict(orient="records")


facilities_service = FacilitiesService()
