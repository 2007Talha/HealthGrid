"""
Unit Tests for Machine Learning Forecasting Models
"""

import pytest
from backend.app.services.ml_forecasting import forecasting_engine

def test_model_training_and_baseline_comparison():
    report = forecasting_engine.train_and_evaluate_models()
    assert report["model_version"] == "swasthya-demand-v1.0"
    
    demand_metrics = report["medicine_demand"]
    # Verify ML model beats baseline
    assert demand_metrics["ml_mae"] < demand_metrics["baseline_mae"], "ML model MAE should be lower than baseline MAE"
    assert demand_metrics["ml_rmse"] < demand_metrics["baseline_rmse"], "ML model RMSE should be lower than baseline RMSE"
    assert demand_metrics["mae_improvement_pct"] > 0, "ML should show positive % improvement over baseline"

def test_multi_horizon_prediction_intervals():
    forecasts = forecasting_engine.forecast_medicine_demand("PHC-BR-PAT-001", "MED-PCM-500", horizon_days=14)
    assert len(forecasts) == 14, "Should generate exactly 14 daily forecast steps"
    
    for step in forecasts:
        p10 = step["lower_bound_p10"]
        p50 = step["predicted_consumption"]
        p90 = step["upper_bound_p90"]
        
        # Verify monotonic quantile ordering: p10 <= p50 <= p90
        assert p10 <= p50, f"Monotonicity violation: p10 ({p10}) > p50 ({p50})"
        assert p50 <= p90, f"Monotonicity violation: p50 ({p50}) > p90 ({p90})"
        assert p50 > 0, "Forecasted consumption must be strictly positive"

def test_footfall_and_bed_forecasts():
    ff_forecasts = forecasting_engine.forecast_patient_footfall("PHC-BR-PAT-001", horizon_days=7)
    assert len(ff_forecasts) == 7
    assert all(f["predicted_footfall"] > 0 for f in ff_forecasts)
    
    bed_forecasts = forecasting_engine.forecast_bed_occupancy("PHC-BR-PAT-001", horizon_days=7)
    assert len(bed_forecasts) == 7
    assert all(0 <= f["predicted_beds_occupied"] <= f["beds_total"] for f in bed_forecasts)
