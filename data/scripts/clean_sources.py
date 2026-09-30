"""
Swasthya Records - Data Cleaning & Standardization Pipeline
Reads raw official government CSVs, applies validation, standardization,
type casting, attaches provenance metadata, logs quality metrics,
and outputs clean datasets to data/processed/government/.
"""

import os
import json
import datetime
from typing import Dict, List, Any
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "raw", "government")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed", "government")
QUALITY_LOG_PATH = os.path.join(BASE_DIR, "data_quality_log.json")

os.makedirs(PROCESSED_DIR, exist_ok=True)

STATE_CODE_MAP = {
    "uttar pradesh": "IN-UP",
    "bihar": "IN-BR",
    "rajasthan": "IN-RJ",
    "maharashtra": "IN-MH",
    "karnataka": "IN-KA",
    "madhya pradesh": "IN-MP",
    "west bengal": "IN-WB",
    "tamil nadu": "IN-TN",
    "gujarat": "IN-GJ",
    "andhra pradesh": "IN-AP",
    "all india / national total": "IN-ALL"
}

quality_report: Dict[str, Any] = {
    "pipeline_execution_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "datasets_processed": {},
    "total_records_processed": 0,
    "total_records_cleaned": 0,
    "quality_anomalies_detected": []
}

def clean_facility_infrastructure():
    raw_path = os.path.join(RAW_DIR, "rhs_health_infrastructure_2022_23.csv")
    df = pd.read_csv(raw_path)
    initial_rows = len(df)
    
    # Strip whitespace & normalize strings
    df["state_name"] = df["state_name"].astype(str).str.strip()
    df["state_code"] = df["state_name"].str.lower().map(STATE_CODE_MAP).fillna("IN-UNKNOWN")
    
    # Numeric sanitization & non-negativity
    int_cols = [
        "sub_centres_functioning", "phcs_functioning", "chcs_functioning",
        "sub_divisional_hospitals", "district_hospitals", "total_phc_beds",
        "total_chc_beds", "total_dh_beds", "phcs_with_regular_power_supply",
        "phcs_with_water_supply", "phcs_with_all_weather_motorable_road"
    ]
    for col in int_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        if (df[col] < 0).any():
            quality_report["quality_anomalies_detected"].append({
                "dataset": "rhs_health_infrastructure_2022_23",
                "issue": f"Negative value detected in column {col}"
            })
            df[col] = df[col].clip(lower=0)

    # Compute derived infrastructure ratios
    df["phc_electrification_rate_pct"] = (df["phcs_with_regular_power_supply"] / df["phcs_functioning"].replace(0, 1) * 100).round(2)
    df["phc_all_weather_road_access_pct"] = (df["phcs_with_all_weather_motorable_road"] / df["phcs_functioning"].replace(0, 1) * 100).round(2)
    
    # Add provenance fields
    df["data_source"] = "OFFICIAL_GOVERNMENT"
    df["provenance_tier"] = "RHS_2022_23"
    df["source_url"] = "https://mohfw.gov.in/sites/default/files/HealthDynamicsOfIndia2022-23.pdf"
    df["retrieved_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    out_path = os.path.join(PROCESSED_DIR, "clean_facility_infrastructure.csv")
    df.to_csv(out_path, index=False)
    
    quality_report["datasets_processed"]["facility_infrastructure"] = {
        "source_file": raw_path,
        "output_file": out_path,
        "initial_rows": initial_rows,
        "processed_rows": len(df),
        "columns_count": len(df.columns),
        "status": "VALIDATED_AND_CLEANED"
    }
    print(f"[CLEAN] Facility Infrastructure: {len(df)} rows -> {out_path}")

def clean_personnel():
    raw_path = os.path.join(RAW_DIR, "rhs_personnel_human_resources_2022_23.csv")
    df = pd.read_csv(raw_path)
    initial_rows = len(df)
    
    df["state_name"] = df["state_name"].astype(str).str.strip()
    df["state_code"] = df["state_name"].str.lower().map(STATE_CODE_MAP).fillna("IN-UNKNOWN")
    
    int_cols = [
        "doctors_at_phcs_sanctioned", "doctors_at_phcs_in_position", "doctors_at_phcs_vacant",
        "specialists_at_chcs_sanctioned", "specialists_at_chcs_in_position", "specialists_at_chcs_vacant",
        "nursing_staff_sanctioned", "nursing_staff_in_position", "anm_sanctioned", "anm_in_position",
        "pharmacists_sanctioned", "pharmacists_in_position"
    ]
    for col in int_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int).clip(lower=0)

    # Derived vacancy and shortfall metrics
    df["doctor_vacancy_rate_pct"] = (df["doctors_at_phcs_vacant"] / df["doctors_at_phcs_sanctioned"].replace(0, 1) * 100).round(2)
    df["specialist_vacancy_rate_pct"] = (df["specialists_at_chcs_vacant"] / df["specialists_at_chcs_sanctioned"].replace(0, 1) * 100).round(2)
    
    # Add provenance fields
    df["data_source"] = "OFFICIAL_GOVERNMENT"
    df["provenance_tier"] = "RHS_2022_23"
    df["source_url"] = "https://mohfw.gov.in/sites/default/files/HealthDynamicsOfIndia2022-23.pdf"
    df["retrieved_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    out_path = os.path.join(PROCESSED_DIR, "clean_personnel.csv")
    df.to_csv(out_path, index=False)
    
    quality_report["datasets_processed"]["personnel"] = {
        "source_file": raw_path,
        "output_file": out_path,
        "initial_rows": initial_rows,
        "processed_rows": len(df),
        "columns_count": len(df.columns),
        "status": "VALIDATED_AND_CLEANED"
    }
    print(f"[CLEAN] Personnel: {len(df)} rows -> {out_path}")

def clean_patient_utilization():
    raw_path = os.path.join(RAW_DIR, "hmis_district_patient_utilization_2022_23.csv")
    df = pd.read_csv(raw_path)
    initial_rows = len(df)
    
    df["state_name"] = df["state_name"].astype(str).str.strip()
    df["state_code"] = df["state_name"].str.lower().map(STATE_CODE_MAP).fillna("IN-UNKNOWN")
    df["district_name"] = df["district_name"].astype(str).str.strip()
    df["district_code"] = df["district_code"].astype(str).str.strip().str.upper()
    
    numeric_cols = [
        "total_opd_allopathic", "total_opd_ayush", "total_ipd_admissions",
        "institutional_deliveries", "fever_syndromic_surveillance_cases",
        "diarrheal_cases_reported", "acute_respiratory_infections_reported"
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int).clip(lower=0)

    # Derived epidemiological indicators
    df["total_opd_combined"] = df["total_opd_allopathic"] + df["total_opd_ayush"]
    df["fever_burden_ratio"] = (df["fever_syndromic_surveillance_cases"] / df["total_opd_combined"].replace(0, 1)).round(4)
    df["ipd_to_opd_ratio"] = (df["total_ipd_admissions"] / df["total_opd_combined"].replace(0, 1)).round(4)
    
    # Add provenance fields
    df["data_source"] = "OFFICIAL_GOVERNMENT"
    df["provenance_tier"] = "HMIS_2022_23"
    df["source_url"] = "https://hmis.mohfw.gov.in/#!/analytical-reports"
    df["retrieved_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    out_path = os.path.join(PROCESSED_DIR, "clean_patient_utilization.csv")
    df.to_csv(out_path, index=False)
    
    quality_report["datasets_processed"]["patient_utilization"] = {
        "source_file": raw_path,
        "output_file": out_path,
        "initial_rows": initial_rows,
        "processed_rows": len(df),
        "columns_count": len(df.columns),
        "status": "VALIDATED_AND_CLEANED"
    }
    print(f"[CLEAN] Patient Utilization: {len(df)} rows -> {out_path}")

def clean_medicine_reference():
    raw_path = os.path.join(RAW_DIR, "nlem_essential_medicines_2022.csv")
    df = pd.read_csv(raw_path)
    initial_rows = len(df)
    
    df["medicine_code"] = df["medicine_code"].astype(str).str.strip().str.upper()
    df["medicine_name"] = df["medicine_name"].astype(str).str.strip()
    df["therapeutic_category"] = df["therapeutic_category"].astype(str).str.strip()
    df["dosage_form"] = df["dosage_form"].astype(str).str.strip()
    df["strength"] = df["strength"].astype(str).str.strip()
    df["route_of_administration"] = df["route_of_administration"].astype(str).str.strip()
    
    # Boolean casting
    bool_cols = ["level_of_healthcare_primary", "level_of_healthcare_secondary", "level_of_healthcare_tertiary", "is_emergency_essential"]
    for col in bool_cols:
        df[col] = df[col].astype(bool)
        
    df["standard_shelf_life_months"] = pd.to_numeric(df["standard_shelf_life_months"], errors="coerce").fillna(24).astype(int)
    
    # Add provenance fields
    df["data_source"] = "OFFICIAL_GOVERNMENT"
    df["provenance_tier"] = "NLEM_2022"
    df["source_url"] = "https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/NLEM_2022.pdf"
    df["retrieved_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    out_path = os.path.join(PROCESSED_DIR, "clean_medicine_reference.csv")
    df.to_csv(out_path, index=False)
    
    quality_report["datasets_processed"]["medicine_reference"] = {
        "source_file": raw_path,
        "output_file": out_path,
        "initial_rows": initial_rows,
        "processed_rows": len(df),
        "columns_count": len(df.columns),
        "status": "VALIDATED_AND_CLEANED"
    }
    print(f"[CLEAN] Medicine Reference: {len(df)} rows -> {out_path}")

def clean_facility_master():
    raw_path = os.path.join(RAW_DIR, "phc_facility_master_registry.csv")
    df = pd.read_csv(raw_path)
    initial_rows = len(df)
    
    df["facility_id"] = df["facility_id"].astype(str).str.strip().str.upper()
    df["facility_name"] = df["facility_name"].astype(str).str.strip()
    df["facility_type"] = df["facility_type"].astype(str).str.strip()
    df["state_name"] = df["state_name"].astype(str).str.strip()
    df["state_code"] = df["state_name"].str.lower().map(STATE_CODE_MAP).fillna("IN-UNKNOWN")
    df["district_name"] = df["district_name"].astype(str).str.strip()
    df["district_code"] = df["district_code"].astype(str).str.strip().str.upper()
    
    # Geographic coordinate validation (India: Lat 8.0 to 37.0, Lon 68.0 to 97.0)
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    
    invalid_coords = df[(df["latitude"] < 8.0) | (df["latitude"] > 37.0) | (df["longitude"] < 68.0) | (df["longitude"] > 97.0)]
    if len(invalid_coords) > 0:
        quality_report["quality_anomalies_detected"].append({
            "dataset": "phc_facility_master_registry",
            "issue": f"{len(invalid_coords)} facilities with out-of-bounds India geo-coordinates."
        })
        
    df["sanctioned_beds"] = pd.to_numeric(df["sanctioned_beds"], errors="coerce").fillna(6).astype(int).clip(lower=0)
    df["catchment_population"] = pd.to_numeric(df["catchment_population"], errors="coerce").fillna(50000).astype(int).clip(lower=0)
    df["sanctioned_doctors"] = pd.to_numeric(df["sanctioned_doctors"], errors="coerce").fillna(2).astype(int).clip(lower=0)
    df["sanctioned_nurses"] = pd.to_numeric(df["sanctioned_nurses"], errors="coerce").fillna(4).astype(int).clip(lower=0)
    df["is_cold_chain_enabled"] = df["is_cold_chain_enabled"].astype(bool)
    df["accessibility_tier"] = df["accessibility_tier"].astype(str).str.strip()
    
    # Add provenance fields
    df["data_source"] = "OFFICIAL_GOVERNMENT"
    df["provenance_tier"] = "NHA_FACILITY_REGISTRY"
    df["source_url"] = "https://facility.abdm.gov.in/"
    df["retrieved_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    out_path = os.path.join(PROCESSED_DIR, "clean_facility_master.csv")
    df.to_csv(out_path, index=False)
    
    quality_report["datasets_processed"]["facility_master"] = {
        "source_file": raw_path,
        "output_file": out_path,
        "initial_rows": initial_rows,
        "processed_rows": len(df),
        "columns_count": len(df.columns),
        "status": "VALIDATED_AND_CLEANED"
    }
    print(f"[CLEAN] Facility Master: {len(df)} rows -> {out_path}")

def main():
    print("Executing Swasthya Records Data Cleaning & Standardization Pipeline...")
    clean_facility_infrastructure()
    clean_personnel()
    clean_patient_utilization()
    clean_medicine_reference()
    clean_facility_master()
    
    total_in = sum(d["initial_rows"] for d in quality_report["datasets_processed"].values())
    total_out = sum(d["processed_rows"] for d in quality_report["datasets_processed"].values())
    quality_report["total_records_processed"] = total_in
    quality_report["total_records_cleaned"] = total_out
    
    with open(QUALITY_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(quality_report, f, indent=2)
        
    print(f"\n[PIPELINE COMPLETE] Cleaned {total_out} records across {len(quality_report['datasets_processed'])} datasets.")
    print(f"Data quality audit log written to: {QUALITY_LOG_PATH}")

if __name__ == "__main__":
    main()
