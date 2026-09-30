"""
Swasthya Records - Predictive Machine Learning & Time-Series Forecasting Engine
Implements:
1. Baseline Model: 7-Day Rolling Moving Average
2. Numerical ML Regressor (Ridge / Regularized GLM) with Feature Standardization
3. Multi-Horizon Forecasting (1-day, 3-day, 7-day, 14-day) with Quantile Prediction Intervals (p10, p50, p90)
4. Comprehensive Model Evaluation vs Baseline (MAE, RMSE, WAPE, R^2)
Model Version: swasthya-demand-v1.0
"""

import logging
import pandas as pd
import numpy as np

from backend.app.services.ml_feature_engineering import feature_pipeline

logger = logging.getLogger("swasthya.ml")

MODEL_VERSION = "swasthya-demand-v1.0"

from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


class RidgeForecaster:
    """Production regularized regressor using scikit-learn Ridge with quantile prediction intervals."""

    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.scaler = StandardScaler()
        self.model = Ridge(alpha=alpha)
        self.residual_std = 1.0
        self.feature_names = []

    def fit(self, X, y, feature_names=None):
        self.feature_names = feature_names or [f"f_{i}" for i in range(X.shape[1])]
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        preds = self.model.predict(X_scaled)
        residuals = y - preds
        self.residual_std = float(np.std(residuals))

    def predict(self, X):
        X_scaled = self.scaler.transform(X)
        raw_preds = self.model.predict(X_scaled)
        return np.clip(raw_preds, a_min=1.0, a_max=None)

    def predict_intervals(self, X):
        """Returns point forecast (p50), lower bound (p10), and upper bound (p90)."""
        point_preds = self.predict(X)
        z_90 = 1.282  # 80% coverage interval
        lower_bound = np.clip(
            point_preds - z_90 * self.residual_std, a_min=0.0, a_max=None
        )
        upper_bound = point_preds + z_90 * self.residual_std
        return lower_bound, point_preds, upper_bound


class ForecastingEngine:
    def __init__(self):
        self.demand_model = RidgeForecaster(alpha=2.5)
        self.footfall_model = RidgeForecaster(alpha=1.5)
        self.bed_model = RidgeForecaster(alpha=1.0)

        self.demand_features = [
            "lag_consumption_1d",
            "lag_consumption_2d",
            "lag_consumption_3d",
            "lag_consumption_7d",
            "lag_consumption_14d",
            "rolling_mean_7d",
            "rolling_std_7d",
            "rolling_mean_14d",
            "day_of_week",
            "is_weekend",
            "is_monday",
            "month",
            "patient_footfall",
            "is_emergency_active",
        ]
        self.footfall_features = [
            "lag_footfall_1d",
            "lag_footfall_2d",
            "lag_footfall_3d",
            "lag_footfall_7d",
            "lag_footfall_14d",
            "rolling_mean_7d",
            "rolling_std_7d",
            "rolling_mean_14d",
            "day_of_week",
            "is_weekend",
            "is_monday",
            "month",
            "is_emergency_active",
        ]
        self.bed_features = [
            "lag_beds_occupied_1d",
            "lag_beds_occupied_2d",
            "lag_beds_occupied_3d",
            "lag_beds_occupied_7d",
            "rolling_mean_7d",
            "day_of_week",
            "is_weekend",
            "is_emergency_active",
        ]

        self.evaluation_report = {}
        self.is_trained = False
        self._history_cache = {}
        self._forecast_cache = {}
        self._latest_date = None

    def clear_cache(self):
        self._history_cache.clear()
        self._forecast_cache.clear()

    def _build_cache(self):
        inv_df = feature_pipeline.inv_df
        if inv_df.empty:
            return
        self._latest_date = pd.to_datetime(inv_df["record_date"].max())
        self._history_cache.clear()

        # Build 14-day history for each phc-medicine
        for (phc, med), group in inv_df.groupby(["phc_id", "medicine_code"]):
            sorted_g = group.sort_values(by="record_date")
            self._history_cache[(phc, med)] = (
                sorted_g["daily_consumption"].tail(14).tolist()
            )

    def train_and_evaluate_models(self):
        """Trains ML models on chronological train split and evaluates against 7-day MA baseline on test split."""
        logger.info("Training forecasting models (%s)...", MODEL_VERSION)

        # 1. Train Medicine Demand Model
        demand_df = feature_pipeline.create_medicine_demand_features()
        train_d, val_d, test_d = feature_pipeline.chronological_split(demand_df)

        X_train_d = train_d[self.demand_features].values
        y_train_d = train_d["daily_consumption"].values
        X_test_d = test_d[self.demand_features].values
        y_test_d = test_d["daily_consumption"].values

        self.demand_model.fit(X_train_d, y_train_d, self.demand_features)

        # Predict on Test Set
        ml_preds_d = self.demand_model.predict(X_test_d)
        baseline_preds_d = test_d[
            "rolling_mean_7d"
        ].values  # 7-day moving average baseline

        # Metrics: Demand
        mae_ml_d = float(np.mean(np.abs(y_test_d - ml_preds_d)))
        mae_base_d = float(np.mean(np.abs(y_test_d - baseline_preds_d)))
        rmse_ml_d = float(np.sqrt(np.mean((y_test_d - ml_preds_d) ** 2)))
        rmse_base_d = float(np.sqrt(np.mean((y_test_d - baseline_preds_d) ** 2)))
        wape_ml_d = float(
            np.sum(np.abs(y_test_d - ml_preds_d)) / np.sum(y_test_d) * 100.0
        )
        wape_base_d = float(
            np.sum(np.abs(y_test_d - baseline_preds_d)) / np.sum(y_test_d) * 100.0
        )

        # 2. Train Patient Footfall Model
        ff_df = feature_pipeline.create_patient_footfall_features()
        train_ff, val_ff, test_ff = feature_pipeline.chronological_split(ff_df)

        X_train_ff = train_ff[self.footfall_features].values
        y_train_ff = train_ff["patient_footfall"].values
        X_test_ff = test_ff[self.footfall_features].values
        y_test_ff = test_ff["patient_footfall"].values

        self.footfall_model.fit(X_train_ff, y_train_ff, self.footfall_features)
        ml_preds_ff = self.footfall_model.predict(X_test_ff)
        base_preds_ff = test_ff["rolling_mean_7d"].values

        mae_ml_ff = float(np.mean(np.abs(y_test_ff - ml_preds_ff)))
        mae_base_ff = float(np.mean(np.abs(y_test_ff - base_preds_ff)))
        rmse_ml_ff = float(np.sqrt(np.mean((y_test_ff - ml_preds_ff) ** 2)))
        rmse_base_ff = float(np.sqrt(np.mean((y_test_ff - base_preds_ff) ** 2)))

        # 3. Train Bed Occupancy Model
        bed_df = feature_pipeline.create_bed_occupancy_features()
        train_b, val_b, test_b = feature_pipeline.chronological_split(bed_df)

        X_train_b = train_b[self.bed_features].values
        y_train_b = train_b["beds_occupied"].values
        X_test_b = test_b[self.bed_features].values
        y_test_b = test_b["beds_occupied"].values

        self.bed_model.fit(X_train_b, y_train_b, self.bed_features)
        ml_preds_b = self.bed_model.predict(X_test_b)
        base_preds_b = test_b["rolling_mean_7d"].values

        mae_ml_b = float(np.mean(np.abs(y_test_b - ml_preds_b)))
        mae_base_b = float(np.mean(np.abs(y_test_b - base_preds_b)))

        self.is_trained = True
        self._build_cache()
        self.evaluation_report = {
            "model_version": MODEL_VERSION,
            "training_samples": len(train_d),
            "test_samples": len(test_d),
            "medicine_demand": {
                "ml_mae": round(mae_ml_d, 2),
                "baseline_mae": round(mae_base_d, 2),
                "ml_rmse": round(rmse_ml_d, 2),
                "baseline_rmse": round(rmse_base_d, 2),
                "ml_wape_pct": round(wape_ml_d, 2),
                "baseline_wape_pct": round(wape_base_d, 2),
                "mae_improvement_pct": round(
                    (mae_base_d - mae_ml_d) / max(0.01, mae_base_d) * 100.0, 2
                ),
            },
            "patient_footfall": {
                "ml_mae": round(mae_ml_ff, 2),
                "baseline_mae": round(mae_base_ff, 2),
                "ml_rmse": round(rmse_ml_ff, 2),
                "baseline_rmse": round(rmse_base_ff, 2),
                "mae_improvement_pct": round(
                    (mae_base_ff - mae_ml_ff) / max(0.01, mae_base_ff) * 100.0, 2
                ),
            },
            "bed_occupancy": {
                "ml_mae": round(mae_ml_b, 2),
                "baseline_mae": round(mae_base_b, 2),
                "mae_improvement_pct": round(
                    (mae_base_b - mae_ml_b) / max(0.01, mae_base_b) * 100.0, 2
                ),
            },
        }
        logger.info(
            "ML Evaluation Complete — Medicine Demand MAE: ML=%.2f vs Baseline=%.2f (%.2f%% improvement)",
            mae_ml_d,
            mae_base_d,
            self.evaluation_report["medicine_demand"]["mae_improvement_pct"],
        )
        return self.evaluation_report

    def forecast_medicine_demand(self, phc_id, medicine_code, horizon_days=14):
        """Generates multi-day demand forecast with p10, p50, p90 intervals for a specific PHC and medicine."""
        cache_key = (phc_id, medicine_code, horizon_days)
        if cache_key in self._forecast_cache:
            return self._forecast_cache[cache_key]

        if not self.is_trained:
            self.train_and_evaluate_models()

        key = (phc_id, medicine_code)
        if key not in self._history_cache:
            self._build_cache()

        history_vals = self._history_cache.get(key)
        if not history_vals:
            return []

        latest_date = self._latest_date or pd.Timestamp("2026-08-23")
        forecasts = []
        sim_history = list(history_vals)
        while len(sim_history) < 14:
            sim_history.insert(0, sim_history[0] if sim_history else 10)

        for h in range(1, horizon_days + 1):
            target_date = latest_date + pd.Timedelta(days=h)
            dow = target_date.dayofweek
            is_weekend = 1 if dow in [5, 6] else 0
            is_monday = 1 if dow == 0 else 0
            month = target_date.month

            # Construct feature vector
            feat_dict = {
                "lag_consumption_1d": sim_history[-1],
                "lag_consumption_2d": sim_history[-2],
                "lag_consumption_3d": sim_history[-3],
                "lag_consumption_7d": sim_history[-7],
                "lag_consumption_14d": sim_history[-14],
                "rolling_mean_7d": np.mean(sim_history[-7:]),
                "rolling_std_7d": np.std(sim_history[-7:]),
                "rolling_mean_14d": np.mean(sim_history[-14:]),
                "day_of_week": dow,
                "is_weekend": is_weekend,
                "is_monday": is_monday,
                "month": month,
                "patient_footfall": int(
                    np.mean(sim_history[-7:]) * 3.5
                ),  # Derived footfall proxy
                "is_emergency_active": 0,
            }

            X_vec = np.array([[feat_dict[f] for f in self.demand_features]])
            p10, p50, p90 = self.demand_model.predict_intervals(X_vec)

            pred_val = float(round(p50[0], 1))
            sim_history.append(pred_val)

            forecasts.append(
                {
                    "horizon_day": h,
                    "target_date": target_date.strftime("%Y-%m-%d"),
                    "predicted_consumption": pred_val,
                    "lower_bound_p10": float(round(p10[0], 1)),
                    "upper_bound_p90": float(round(p90[0], 1)),
                    "model_version": MODEL_VERSION,
                }
            )

        self._forecast_cache[cache_key] = forecasts
        return forecasts

    def forecast_patient_footfall(self, phc_id, horizon_days=7):
        """Generates patient footfall forecast for 1 to 7 days."""
        if not self.is_trained:
            self.train_and_evaluate_models()

        fac_df = feature_pipeline.fac_df
        phc_df = fac_df[fac_df["phc_id"] == phc_id].sort_values(by="record_date")
        if phc_df.empty:
            return []

        latest_row = phc_df.iloc[-1]
        latest_date = pd.to_datetime(latest_row["record_date"])
        history_vals = phc_df["patient_footfall"].tail(14).values.tolist()

        forecasts = []
        sim_history = list(history_vals)
        while len(sim_history) < 14:
            sim_history.insert(0, sim_history[0] if sim_history else 100)

        for h in range(1, horizon_days + 1):
            target_date = latest_date + pd.Timedelta(days=h)
            dow = target_date.dayofweek
            feat_dict = {
                "lag_footfall_1d": sim_history[-1],
                "lag_footfall_2d": sim_history[-2],
                "lag_footfall_3d": sim_history[-3],
                "lag_footfall_7d": sim_history[-7],
                "lag_footfall_14d": sim_history[-14],
                "rolling_mean_7d": np.mean(sim_history[-7:]),
                "rolling_std_7d": np.std(sim_history[-7:]),
                "rolling_mean_14d": np.mean(sim_history[-14:]),
                "day_of_week": dow,
                "is_weekend": 1 if dow in [5, 6] else 0,
                "is_monday": 1 if dow == 0 else 0,
                "month": target_date.month,
                "is_emergency_active": 0,
            }
            X_vec = np.array([[feat_dict[f] for f in self.footfall_features]])
            p10, p50, p90 = self.footfall_model.predict_intervals(X_vec)

            pred_val = int(round(p50[0]))
            sim_history.append(pred_val)

            forecasts.append(
                {
                    "horizon_day": h,
                    "target_date": target_date.strftime("%Y-%m-%d"),
                    "predicted_footfall": pred_val,
                    "lower_bound_p10": int(round(p10[0])),
                    "upper_bound_p90": int(round(p90[0])),
                    "model_version": MODEL_VERSION,
                }
            )

        return forecasts

    def forecast_bed_occupancy(self, phc_id, horizon_days=7):
        """Generates bed occupancy forecast for 1 to 7 days."""
        if not self.is_trained:
            self.train_and_evaluate_models()

        fac_df = feature_pipeline.fac_df
        phc_df = fac_df[fac_df["phc_id"] == phc_id].sort_values(by="record_date")
        if phc_df.empty:
            return []

        latest_row = phc_df.iloc[-1]
        sanctioned_beds = int(latest_row["beds_total"])
        latest_date = pd.to_datetime(latest_row["record_date"])
        history_vals = phc_df["beds_occupied"].tail(7).values.tolist()

        forecasts = []
        sim_history = list(history_vals)
        while len(sim_history) < 7:
            sim_history.insert(0, sim_history[0] if sim_history else 5)

        for h in range(1, horizon_days + 1):
            target_date = latest_date + pd.Timedelta(days=h)
            dow = target_date.dayofweek
            feat_dict = {
                "lag_beds_occupied_1d": sim_history[-1],
                "lag_beds_occupied_2d": sim_history[-2],
                "lag_beds_occupied_3d": sim_history[-3],
                "lag_beds_occupied_7d": sim_history[-7],
                "rolling_mean_7d": np.mean(sim_history[-7:]),
                "day_of_week": dow,
                "is_weekend": 1 if dow in [5, 6] else 0,
                "is_emergency_active": 0,
            }
            X_vec = np.array([[feat_dict[f] for f in self.bed_features]])
            _, p50, _ = self.bed_model.predict_intervals(X_vec)

            pred_val = min(sanctioned_beds, max(0, int(round(p50[0]))))
            sim_history.append(pred_val)
            occ_rate = round(
                (pred_val / sanctioned_beds * 100.0) if sanctioned_beds > 0 else 0.0, 2
            )

            forecasts.append(
                {
                    "horizon_day": h,
                    "target_date": target_date.strftime("%Y-%m-%d"),
                    "predicted_beds_occupied": pred_val,
                    "beds_total": sanctioned_beds,
                    "predicted_occupancy_rate_pct": occ_rate,
                    "model_version": MODEL_VERSION,
                }
            )

        return forecasts


forecasting_engine = ForecastingEngine()
