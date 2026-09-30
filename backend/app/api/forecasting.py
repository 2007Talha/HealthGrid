"""
Swasthya Records - Forecasting API Endpoints
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from backend.app.services.ml_forecasting import forecasting_engine

router = APIRouter()

@router.get("/medicine/{phc_id}/{medicine_code}", summary="Get multi-day ML demand forecast with p10, p50, p90 prediction intervals")
def get_medicine_forecast(
    phc_id: str,
    medicine_code: str,
    horizon_days: int = Query(default=14, ge=1, le=30, description="Forecast horizon in days")
):
    forecasts = forecasting_engine.forecast_medicine_demand(phc_id, medicine_code, horizon_days=horizon_days)
    if not forecasts:
        raise HTTPException(status_code=404, detail=f"No forecast available for {phc_id} - {medicine_code}")
    return {
        "phc_id": phc_id,
        "medicine_code": medicine_code,
        "horizon_days": horizon_days,
        "model_version": forecasts[0]["model_version"],
        "forecasts": forecasts
    }

@router.get("/patients/{phc_id}", summary="Get 1 to 7 day patient footfall forecast with confidence bounds")
def get_patient_footfall_forecast(
    phc_id: str,
    horizon_days: int = Query(default=7, ge=1, le=14)
):
    forecasts = forecasting_engine.forecast_patient_footfall(phc_id, horizon_days=horizon_days)
    if not forecasts:
        raise HTTPException(status_code=404, detail=f"No footfall forecast available for {phc_id}")
    return {
        "phc_id": phc_id,
        "horizon_days": horizon_days,
        "forecasts": forecasts
    }

@router.get("/beds/{phc_id}", summary="Get 1 to 7 day bed occupancy forecast")
def get_bed_occupancy_forecast(
    phc_id: str,
    horizon_days: int = Query(default=7, ge=1, le=14)
):
    forecasts = forecasting_engine.forecast_bed_occupancy(phc_id, horizon_days=horizon_days)
    if not forecasts:
        raise HTTPException(status_code=404, detail=f"No bed forecast available for {phc_id}")
    return {
        "phc_id": phc_id,
        "horizon_days": horizon_days,
        "forecasts": forecasts
    }

@router.get("/evaluation-metrics", summary="Get model evaluation metrics vs 7-day moving average baseline")
def get_model_evaluation_metrics():
    if not forecasting_engine.is_trained:
        forecasting_engine.train_and_evaluate_models()
    return forecasting_engine.evaluation_report
