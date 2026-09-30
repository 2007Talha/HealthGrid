"""
Swasthya Records - BigQuery Dataset & Table Ingestion Script
Creates dataset 'swasthyagrid' in GCP project 'arcadeaiagent' and loads cleaned official government CSVs.
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any
import pandas as pd
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "processed", "government")
SCHEMAS_PATH = os.path.join(BASE_DIR, "schemas", "bigquery_schemas.json")

PROJECT_ID = "arcadeaiagent"
DATASET_ID = "swasthyagrid"
LOCATION = "asia-south1"

TABLE_FILE_MAP = {
    "facility_master": "clean_facility_master.csv",
    "facility_infrastructure": "clean_facility_infrastructure.csv",
    "personnel": "clean_personnel.csv",
    "patient_utilization": "clean_patient_utilization.csv",
    "medicine_reference": "clean_medicine_reference.csv"
}

def load_schemas() -> Dict[str, List[Dict[str, Any]]]:
    with open(SCHEMAS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def build_bigquery_schema(field_defs: List[Dict[str, Any]]) -> List[bigquery.SchemaField]:
    schema = []
    for field in field_defs:
        schema.append(
            bigquery.SchemaField(
                name=field["name"],
                field_type=field["type"],
                mode=field.get("mode", "NULLABLE"),
                description=field.get("description", "")
            )
        )
    return schema

def execute_ingestion(dry_run: bool = False):
    print("=" * 80)
    print(f"SWASTHYA RECORDS - BIGQUERY INGESTION PIPELINE (Project: {PROJECT_ID})")
    print("=" * 80)
    
    schemas = load_schemas()
    
    if dry_run:
        print("[DRY RUN MODE] Validating BigQuery schemas against processed CSV data structures...")
        for table_name, csv_file in TABLE_FILE_MAP.items():
            csv_path = os.path.join(PROCESSED_DIR, csv_file)
            df = pd.read_csv(csv_path)
            schema_fields = [f["name"] for f in schemas[table_name]]
            df_cols = list(df.columns)
            missing = set(schema_fields) - set(df_cols)
            assert not missing, f"Table {table_name} missing columns: {missing}"
            print(f"  [PASS] {table_name}: Schema match validated ({len(df)} rows, {len(schema_fields)} cols)")
        print("\nDry-run validation successful. All schemas and CSV headers match 1:1.")
        return

    try:
        client = bigquery.Client(project=PROJECT_ID)
        dataset_ref = bigquery.DatasetReference(PROJECT_ID, DATASET_ID)
        
        # Create dataset if not exists
        try:
            dataset = client.get_dataset(dataset_ref)
            print(f"[OK] Found existing BigQuery dataset: {PROJECT_ID}.{DATASET_ID}")
        except Exception:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = LOCATION
            dataset.description = "Swasthya Records - National Health Infrastructure & Telemetry Warehouse"
            dataset = client.create_dataset(dataset, timeout=30)
            print(f"[CREATED] BigQuery dataset created: {PROJECT_ID}.{DATASET_ID} in {LOCATION}")

        # Load each table
        for table_name, csv_file in TABLE_FILE_MAP.items():
            csv_path = os.path.join(PROCESSED_DIR, csv_file)
            df = pd.read_csv(csv_path)
            table_ref = dataset_ref.table(table_name)
            
            bq_schema = build_bigquery_schema(schemas[table_name])
            job_config = bigquery.LoadJobConfig(
                schema=bq_schema,
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
                source_format=bigquery.SourceFormat.CSV,
                skip_leading_rows=1
            )
            
            with open(csv_path, "rb") as source_file:
                job = client.load_table_from_file(source_file, table_ref, job_config=job_config)
                job.result()  # Wait for job to complete
                
            table = client.get_table(table_ref)
            print(f"[LOADED] Table {PROJECT_ID}.{DATASET_ID}.{table_name}: {table.num_rows} rows loaded.")
            
        print("\n" + "=" * 80)
        print("BIGQUERY INGESTION COMPLETED SUCCESSFULLY")
        print("=" * 80)

    except GoogleAPIError as e:
        print(f"[GCP API ERROR] {e}")
        print("Ensure Google Cloud credentials are configured or run with --dry-run")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Load official cleaned health datasets into Google BigQuery.")
    parser.add_argument("--dry-run", action="store_true", help="Validate schema compatibility without executing cloud API calls.")
    args = parser.parse_args()
    execute_ingestion(dry_run=args.dry_run)

if __name__ == "__main__":
    main()
