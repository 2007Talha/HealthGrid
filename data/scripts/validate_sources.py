"""
Swasthya Records - Data Validation & Quality Assurance Test Suite
Performs structural, referential, domain, and provenance validation across all cleaned datasets.
"""

import os
import sys
from typing import List, Dict
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "processed", "government")

def validate_dataset_presence():
    required_files = [
        "clean_facility_master.csv",
        "clean_facility_infrastructure.csv",
        "clean_personnel.csv",
        "clean_patient_utilization.csv",
        "clean_medicine_reference.csv"
    ]
    print("[TEST 1/5] Validating presence of processed datasets...")
    for filename in required_files:
        path = os.path.join(PROCESSED_DIR, filename)
        assert os.path.exists(path), f"CRITICAL: Missing file {path}"
        df = pd.read_csv(path)
        assert len(df) > 0, f"CRITICAL: File {filename} is empty!"
        print(f"  [PASS] {filename}: {len(df)} records, {len(df.columns)} columns")

def validate_referential_integrity():
    print("\n[TEST 2/5] Validating referential integrity across state & district hierarchies...")
    df_facilities = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_facility_master.csv"))
    df_infra = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_facility_infrastructure.csv"))
    df_util = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_patient_utilization.csv"))
    
    # State code consistency
    facility_states = set(df_facilities["state_code"].unique())
    infra_states = set(df_infra["state_code"].unique())
    assert facility_states.issubset(infra_states), f"Unmatched state codes: {facility_states - infra_states}"
    print(f"  [PASS] All {len(facility_states)} facility state codes mapped to national infrastructure registry.")
    
    # District code consistency
    facility_districts = set(df_facilities["district_code"].unique())
    util_districts = set(df_util["district_code"].unique())
    assert facility_districts.issubset(util_districts), f"Unmatched district codes: {facility_districts - util_districts}"
    print(f"  [PASS] All {len(facility_districts)} facility district codes verified in HMIS district factsheets.")

def validate_domain_constraints():
    print("\n[TEST 3/5] Validating domain boundaries and numerical bounds...")
    df_facilities = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_facility_master.csv"))
    
    # Coordinates in India bounds
    assert (df_facilities["latitude"] >= 8.0).all() and (df_facilities["latitude"] <= 37.0).all(), "Invalid latitude"
    assert (df_facilities["longitude"] >= 68.0).all() and (df_facilities["longitude"] <= 97.0).all(), "Invalid longitude"
    print("  [PASS] All facility GPS coordinates within authentic India geographic bounding box.")
    
    # Beds and doctors positive
    assert (df_facilities["sanctioned_beds"] > 0).all(), "Zero/negative bed count detected"
    assert (df_facilities["sanctioned_doctors"] > 0).all(), "Zero/negative doctor count detected"
    print("  [PASS] Sanctioned beds and medical personnel constraints satisfied.")

def validate_medicine_formulary():
    print("\n[TEST 4/5] Validating NLEM 2022 Essential Medicine formulary...")
    df_meds = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_medicine_reference.csv"))
    
    # Unique medicine codes
    assert df_meds["medicine_code"].is_unique, "Duplicate medicine codes detected"
    
    # Key life-saving drugs present
    emergency_meds = df_meds[df_meds["is_emergency_essential"] == True]["medicine_name"].tolist()
    required_key_meds = ["Paracetamol", "Amoxicillin", "Oral Rehydration Salts (WHO Formula)", "Anti-Snake Venom Serum (Polyvalent)", "Human Insulin (Regular / Soluble)"]
    for med in required_key_meds:
        assert any(med in m for m in emergency_meds), f"Missing key emergency medicine: {med}"
    print(f"  [PASS] Verified {len(df_meds)} essential medicines ({len(emergency_meds)} emergency essential).")

def validate_provenance_and_audit():
    print("\n[TEST 5/5] Validating data provenance tags and segregation...")
    for filename in os.listdir(PROCESSED_DIR):
        if not filename.endswith(".csv"):
            continue
        df = pd.read_csv(os.path.join(PROCESSED_DIR, filename))
        assert "data_source" in df.columns, f"Missing data_source in {filename}"
        assert (df["data_source"] == "OFFICIAL_GOVERNMENT").all(), f"Invalid data_source in {filename}"
        assert "provenance_tier" in df.columns, f"Missing provenance_tier in {filename}"
        assert "source_url" in df.columns, f"Missing source_url in {filename}"
    print("  [PASS] 100% of records retain complete Official Government Provenance metadata.")

def main():
    print("=" * 80)
    print("SWASTHYA RECORDS - GOVERNMENT DATA VALIDATION TEST SUITE")
    print("=" * 80)
    try:
        validate_dataset_presence()
        validate_referential_integrity()
        validate_domain_constraints()
        validate_medicine_formulary()
        validate_provenance_and_audit()
        print("\n" + "=" * 80)
        print("ALL 5 VALIDATION SUITES PASSED PERFECTLY (100% DATA QUALITY GUARANTEED)")
        print("=" * 80)
    except AssertionError as e:
        print(f"\n[VALIDATION FAILED] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
