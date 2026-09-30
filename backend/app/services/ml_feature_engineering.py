"""
Swasthya Records - Feature Engineering & Chronological Split Pipeline
Prepares time-series feature matrices from operational logs for demand, footfall, and bed forecasting.
Ensures strict chronological splitting to eliminate data leakage.
"""

import os
import logging
import numpy as np
import pandas as pd

from backend.app.core.config import settings

logger = logging.getLogger("swasthya.ml_features")


class FeatureEngineeringPipeline:
    """Pipeline for ingesting operational logs, engineering time-series features,
    and generating leakage-free chronological train/val/test splits.
    """

    DEFAULT_LAG_DAYS = [1, 2, 3, 7, 14]
    ROLLING_WINDOWS = [(7, 3), (14, 7)]  # (window, min_periods)

    def __init__(self, auto_load=True):
        self._fac_df = None
        self._inv_df = None
        if auto_load:
            self._load_data(raise_on_missing=False)

    @property
    def fac_df(self):
        if self._fac_df is None:
            self._load_data(raise_on_missing=True)
        return self._fac_df

    @fac_df.setter
    def fac_df(self, df):
        self._fac_df = df

    @property
    def inv_df(self):
        if self._inv_df is None:
            self._load_data(raise_on_missing=True)
        return self._inv_df

    @inv_df.setter
    def inv_df(self, df):
        self._inv_df = df

    def _load_data(self, raise_on_missing=False):
        """Loads and deduplicates daily operational and medicine inventory logs."""
        fac_path = os.path.join(settings.SIM_DATA_DIR, "phc_operational_daily.csv")
        inv_path = os.path.join(settings.SIM_DATA_DIR, "medicine_inventory_daily.csv")

        if os.path.exists(fac_path) and os.path.exists(inv_path):
            fac = pd.read_csv(fac_path)
            inv = pd.read_csv(inv_path)

            fac["record_date"] = pd.to_datetime(fac["record_date"])
            inv["record_date"] = pd.to_datetime(inv["record_date"])

            # Deduplicate by primary key to prevent Cartesian explosion on joins
            fac = fac.drop_duplicates(subset=["phc_id", "record_date"], keep="last")
            inv = inv.drop_duplicates(
                subset=["phc_id", "medicine_code", "record_date"], keep="last"
            )

            self._fac_df = fac.sort_values(by=["phc_id", "record_date"]).reset_index(
                drop=True
            )
            self._inv_df = inv.sort_values(
                by=["phc_id", "medicine_code", "record_date"]
            ).reset_index(drop=True)
            logger.info(
                "Loaded and deduplicated operational data: %d fac rows, %d inv rows",
                len(self._fac_df),
                len(self._inv_df),
            )
        else:
            msg = f"Operational data not found at {settings.SIM_DATA_DIR}. Run Phase 2 simulation first."
            if raise_on_missing:
                raise FileNotFoundError(msg)
            logger.warning(msg)
            self._fac_df = pd.DataFrame()
            self._inv_df = pd.DataFrame()

    @staticmethod
    def _add_calendar_features(df, date_col="record_date"):
        """Extracts deterministic temporal calendar features from record dates."""
        df = df.copy()
        dates = pd.to_datetime(df[date_col])
        df["day_of_week"] = dates.dt.dayofweek
        df["day_of_month"] = dates.dt.day
        df["month"] = dates.dt.month
        df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
        df["is_monday"] = (df["day_of_week"] == 0).astype(int)
        return df

    @staticmethod
    def _add_lag_features(
        df,
        group_cols,
        target_col,
        lags,
        prefix,
    ):
        """Computes lagged values grouped by the specified hierarchy."""
        df = df.copy()
        for lag in lags:
            df[f"{prefix}_{lag}d"] = df.groupby(group_cols)[target_col].shift(lag)
        return df

    @staticmethod
    def _add_rolling_features(
        df,
        group_cols,
        target_col,
        windows,
        prefix,
    ):
        """Computes shifted rolling summary metrics (mean, std) to avoid target leakage."""
        df = df.copy()
        grouped_shifted = df.groupby(group_cols)[target_col].shift(1)
        for window, min_periods in windows:
            df[f"{prefix}_mean_{window}d"] = grouped_shifted.rolling(
                window, min_periods=min_periods
            ).mean()
            if window == 7:
                df[f"{prefix}_std_{window}d"] = (
                    grouped_shifted.rolling(window, min_periods=min_periods)
                    .std()
                    .fillna(0.0)
                )
        return df

    def create_medicine_demand_features(self):
        """Constructs lag, rolling, calendar, and facility features for medicine demand forecasting."""
        df = self.inv_df.copy()
        if df.empty:
            return pd.DataFrame()

        df = df.sort_values(by=["phc_id", "medicine_code", "record_date"]).reset_index(
            drop=True
        )

        # Merge facility operational context (footfall, occupancy, emergency)
        fac_cols = [
            "phc_id",
            "record_date",
            "patient_footfall",
            "beds_occupied",
            "emergency_status",
        ]
        fac_meta = self.fac_df[fac_cols].copy()
        df = pd.merge(df, fac_meta, on=["phc_id", "record_date"], how="left")

        # Calendar features
        df = self._add_calendar_features(df)

        # Lag features
        df = self._add_lag_features(
            df,
            group_cols=["phc_id", "medicine_code"],
            target_col="daily_consumption",
            lags=self.DEFAULT_LAG_DAYS,
            prefix="lag_consumption",
        )

        # Rolling moving statistics
        df = self._add_rolling_features(
            df,
            group_cols=["phc_id", "medicine_code"],
            target_col="daily_consumption",
            windows=self.ROLLING_WINDOWS,
            prefix="rolling",
        )

        # Emergency & contextual imputation
        df["is_emergency_active"] = (df["emergency_status"] != "NORMAL").astype(int)
        df["patient_footfall"] = df["patient_footfall"].fillna(100.0)

        # Filter initial window NaNs if sufficient history exists
        if df["record_date"].nunique() > 20:
            df = df.dropna(subset=["lag_consumption_14d", "rolling_mean_14d"])
        else:
            df = df.bfill().fillna(10.0)

        return df.reset_index(drop=True)

    def create_patient_footfall_features(self):
        """Constructs features for patient footfall forecasting."""
        df = self.fac_df.copy()
        if df.empty:
            return pd.DataFrame()

        df = df.sort_values(by=["phc_id", "record_date"]).reset_index(drop=True)
        df = self._add_calendar_features(df)

        df = self._add_lag_features(
            df,
            group_cols=["phc_id"],
            target_col="patient_footfall",
            lags=self.DEFAULT_LAG_DAYS,
            prefix="lag_footfall",
        )

        df = self._add_rolling_features(
            df,
            group_cols=["phc_id"],
            target_col="patient_footfall",
            windows=self.ROLLING_WINDOWS,
            prefix="rolling",
        )

        df["is_emergency_active"] = (df["emergency_status"] != "NORMAL").astype(int)

        if df["record_date"].nunique() > 20:
            df = df.dropna(subset=["lag_footfall_14d", "rolling_mean_14d"])
        else:
            df = df.bfill().fillna(100.0)

        return df.reset_index(drop=True)

    def create_bed_occupancy_features(self):
        """Constructs features for bed occupancy forecasting."""
        df = self.fac_df.copy()
        if df.empty:
            return pd.DataFrame()

        df = df.sort_values(by=["phc_id", "record_date"]).reset_index(drop=True)
        df = self._add_calendar_features(df)

        df = self._add_lag_features(
            df,
            group_cols=["phc_id"],
            target_col="beds_occupied",
            lags=[1, 2, 3, 7],
            prefix="lag_beds_occupied",
        )

        df = self._add_rolling_features(
            df,
            group_cols=["phc_id"],
            target_col="beds_occupied",
            windows=[(7, 3)],
            prefix="rolling",
        )

        df["is_emergency_active"] = (df["emergency_status"] != "NORMAL").astype(int)

        if df["record_date"].nunique() > 20:
            df = df.dropna(subset=["lag_beds_occupied_7d", "rolling_mean_7d"])
        else:
            df = df.bfill().fillna(5.0)

        return df.reset_index(drop=True)

    def chronological_split(self, df, train_pct=0.70, val_pct=0.15):
        """Splits time-series chronologically into Train, Validation, and Test sets.
        Guarantees that train_dates < val_dates < test_dates to prevent data leakage.
        """
        if df.empty:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        dates = np.sort(df["record_date"].unique())
        n_dates = len(dates)

        if n_dates < 3:
            return df.copy(), df.copy(), df.copy()

        train_idx = max(1, int(n_dates * train_pct))
        val_idx = max(train_idx + 1, int(n_dates * (train_pct + val_pct)))

        if val_idx >= n_dates:
            val_idx = n_dates - 1
        if train_idx >= val_idx:
            train_idx = val_idx - 1

        train_dates = dates[:train_idx]
        val_dates = dates[train_idx:val_idx]
        test_dates = dates[val_idx:]

        train_df = df[df["record_date"].isin(train_dates)].copy()
        val_df = df[df["record_date"].isin(val_dates)].copy()
        test_df = df[df["record_date"].isin(test_dates)].copy()

        return train_df, val_df, test_df


feature_pipeline = FeatureEngineeringPipeline()
