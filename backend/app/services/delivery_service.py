import os
import pandas as pd
from backend.app.core.config import settings


class DeliveryService:
    def __init__(self):
        self._del_df = None
        self._in_transit_all = None
        self._in_transit_by_phc = {}

    def clear_cache(self):
        self._del_df = None
        self._in_transit_all = None
        self._in_transit_by_phc.clear()

    def _ensure_loaded(self):
        if self._del_df is not None:
            return
        csv_path = os.path.join(settings.SIM_DATA_DIR, "medicine_deliveries.csv")
        if os.path.exists(csv_path):
            try:
                self._del_df = pd.read_csv(csv_path)
            except Exception:
                self._del_df = pd.DataFrame()
        else:
            self._del_df = pd.DataFrame()

        if not self._del_df.empty and "status" in self._del_df.columns:
            in_transit_df = self._del_df[self._del_df["status"] == "IN_TRANSIT"].fillna(
                ""
            )
            self._in_transit_all = in_transit_df.to_dict(orient="records")
            for phc, group in in_transit_df.groupby("phc_id"):
                self._in_transit_by_phc[str(phc)] = group.to_dict(orient="records")
        else:
            self._in_transit_all = []

    def _get_df(self):
        self._ensure_loaded()
        return self._del_df if self._del_df is not None else pd.DataFrame()

    def get_in_transit_deliveries(self, phc_id=None):
        self._ensure_loaded()
        if phc_id:
            return self._in_transit_by_phc.get(phc_id, [])
        return self._in_transit_all or []

    def get_incoming_deliveries(self, phc_id=None, max_eta_days=7):
        return self.get_in_transit_deliveries(phc_id)

    def get_recent_deliveries(self, limit=50):
        df = self._get_df()
        if df.empty:
            return []
        return df.tail(limit).fillna("").to_dict(orient="records")


delivery_service = DeliveryService()
