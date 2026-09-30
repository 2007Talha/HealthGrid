"""
Swasthya Records - BigQuery Predictive Layer Ingestion Script
Batches and stores model forecasts, stock-out evaluations, early warning alerts, and model metadata into BigQuery dataset arcadeaiagent.swasthyagrid.
"""

import os
import json
import datetime
import pandas as pd
from google.cloud import bigquery
from backend.app.core.config import settings
from backend.app.services.ml_forecasting import forecasting_engine
from backend.app.services.risk_engine import risk_engine
from backend.app.services.alert_engine import alert_engine

def export_and_load_predictions():
    print("[BIGQUERY EXPORT] Batch generating predictions and alerts for BigQuery...")
    
    out_dir = os.path.join(settings.DATA_DIR, "processed", "forecasts")
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Model Metadata & Evaluation Report
    eval_report = forecasting_engine.train_and_evaluate_models()
    meta_records = [{
        "model_version": eval_report["model_version"],
        "training_samples": eval_report["training_samples"],
        "test_samples": eval_report["test_samples"],
        "medicine_demand_mae": eval_report["medicine_demand"]["ml_mae"],
        "medicine_demand_baseline_mae": eval_report["medicine_demand"]["baseline_mae"],
        "mae_improvement_pct": eval_report["medicine_demand"]["mae_improvement_pct"],
        "patient_footfall_mae": eval_report["patient_footfall"]["ml_mae"],
        "bed_occupancy_mae": eval_report["bed_occupancy"]["ml_mae"],
        "trained_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }]
    meta_df = pd.DataFrame(meta_records)
    meta_path = os.path.join(out_dir, "model_metadata.csv")
    meta_df.to_csv(meta_path, index=False)
    
    # 2. Multi-horizon Demand Forecasts
    all_risks = risk_engine.evaluate_all_facility_risks()
    forecast_rows = []
    risk_rows = []
    
    for r in all_risks:
        risk_rows.append({
            "phc_id": r["phc_id"],
            "facility_name": r["facility_name"],
            "medicine_code": r["medicine_code"],
            "medicine_name": r["medicine_name"],
            "therapeutic_category": r["therapeutic_category"],
            "current_stock": r["current_stock"],
            "average_daily_predicted_demand": r["average_daily_predicted_demand"],
            "days_of_stock_available": r["days_of_stock_available"],
            "safety_stock_threshold": r["safety_stock_threshold"],
            "risk_level": r["risk_level"],
            "projected_stockout_date": r["projected_stockout_date"] or "NONE",
            "anomaly_detected": r["anomaly_detected"],
            "model_version": r["model_version"],
            "evaluated_at": r["evaluated_at"]
        })
        for step in r.get("projected_trajectory", []):
            forecast_rows.append({
                "phc_id": r["phc_id"],
                "medicine_code": r["medicine_code"],
                "target_date": step["date"],
                "predicted_consumption": step["predicted_consumption"],
                "incoming_deliveries": step["incoming_deliveries"],
                "projected_closing_stock": step["projected_closing_stock"],
                "model_version": r["model_version"]
            })
            
    risk_df = pd.DataFrame(risk_rows)
    risk_path = os.path.join(out_dir, "stock_risk_evaluations.csv")
    risk_df.to_csv(risk_path, index=False)
    
    forecast_df = pd.DataFrame(forecast_rows)
    forecast_path = os.path.join(out_dir, "demand_forecasts.csv")
    forecast_df.to_csv(forecast_path, index=False)
    
    # 3. Active Early Warning Alerts
    alerts = alert_engine.generate_all_active_alerts(min_severity="WARNING")
    alerts_clean = []
    for a in alerts:
        alerts_clean.append({
            "alert_id": a["alert_id"],
            "severity": a["severity"],
            "alert_type": a["alert_type"],
            "facility_id": a["facility_id"],
            "facility_name": a["facility_name"],
            "resource_id": a["resource_id"],
            "resource_name": a["resource_name"],
            "evidence_summary": a["evidence_summary"],
            "projected_impact": a["projected_impact"],
            "recommended_next_step": a["recommended_next_step"],
            "created_at": a["created_at"],
            "status": a["status"]
        })
    alerts_df = pd.DataFrame(alerts_clean)
    alerts_path = os.path.join(out_dir, "early_warning_alerts.csv")
    alerts_df.to_csv(alerts_path, index=False)
    
    print(f"[EXPORT COMPLETE] Generated:\n - {meta_path} ({len(meta_df)} rows)\n - {risk_path} ({len(risk_df)} rows)\n - {forecast_path} ({len(forecast_df)} rows)\n - {alerts_path} ({len(alerts_df)} rows)")

    # 4. Ingest into BigQuery using bq tool or Python SDK
    tables = [
        ("model_metadata", meta_path),
        ("stock_risk_evaluations", risk_path),
        ("demand_forecasts", forecast_path),
        ("early_warning_alerts", alerts_path)
    ]
    
    for table_name, csv_file in tables:
        cmd = f'bq load --autodetect --replace --source_format=CSV --skip_leading_rows=1 {settings.GCP_PROJECT_ID}:{settings.BIGQUERY_DATASET}.{table_name} "{csv_file}"'
        print(f"[BQ LOAD] Loading {table_name} into {settings.GCP_PROJECT_ID}:{settings.BIGQUERY_DATASET}...")
        os.system(cmd)

if __name__ == "__main__":
    export_and_load_predictions()
