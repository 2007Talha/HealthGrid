"""
Swasthya Records - Government Data Discovery & Registry
Catalog metadata for official Indian healthcare datasets from data.gov.in / MoHFW.
"""

import json
from typing import Dict, Any

DATASET_CATALOG: Dict[str, Dict[str, Any]] = {
    "rhs_infrastructure_2022_23": {
        "official_dataset_name": "Health Dynamics of India (Infrastructure and Human Resources) 2022-23 - Health Infrastructure Statistics",
        "publisher": "Ministry of Health & Family Welfare (MoHFW), Statistics Division, Government of India",
        "catalog_url": "https://data.gov.in/keywords/rural-health-statistics",
        "official_source_url": "https://mohfw.gov.in/sites/default/files/HealthDynamicsOfIndia2022-23.pdf",
        "publication_date": "2024-09-18",
        "last_updated_date": "2024-09-18",
        "temporal_coverage": "2022-2023 (Status as of March 31, 2023)",
        "spatial_coverage": "National (All Indian States & Union Territories)",
        "granularity": "State & District aggregates of Primary Healthcare Institutions",
        "provenance_tier": "OFFICIAL_GOVERNMENT",
        "official_columns": [
            "state_name", "sub_centres_functioning", "phcs_functioning",
            "chcs_functioning", "sub_divisional_hospitals", "district_hospitals",
            "total_phc_beds", "total_chc_beds", "total_dh_beds",
            "phcs_with_regular_power_supply", "phcs_with_water_supply", "phcs_with_all_weather_motorable_road"
        ],
        "data_api_available": False,
        "download_format": "PDF / CSV Data Tables",
        "licensing": "Government Open Data License - India (GODL)",
        "notes": "Renamed from 'Rural Health Statistics (RHS)' to 'Health Dynamics of India'. Contains ground-truth infrastructure capacities."
    },
    "rhs_personnel_2022_23": {
        "official_dataset_name": "Health Dynamics of India (Infrastructure and Human Resources) 2022-23 - Healthcare Human Resources",
        "publisher": "Ministry of Health & Family Welfare (MoHFW), Statistics Division, Government of India",
        "catalog_url": "https://data.gov.in/keywords/health-manpower",
        "official_source_url": "https://mohfw.gov.in/sites/default/files/HealthDynamicsOfIndia2022-23.pdf",
        "publication_date": "2024-09-18",
        "last_updated_date": "2024-09-18",
        "temporal_coverage": "2022-2023",
        "spatial_coverage": "National (All States & UTs)",
        "granularity": "State-wise Sanctioned, In-Position, Vacant, and Shortfall counts",
        "provenance_tier": "OFFICIAL_GOVERNMENT",
        "official_columns": [
            "state_name", "doctors_at_phcs_sanctioned", "doctors_at_phcs_in_position",
            "doctors_at_phcs_vacant", "specialists_at_chcs_sanctioned", "specialists_at_chcs_in_position",
            "specialists_at_chcs_vacant", "nursing_staff_sanctioned", "nursing_staff_in_position",
            "anm_sanctioned", "anm_in_position", "pharmacists_sanctioned", "pharmacists_in_position"
        ],
        "data_api_available": False,
        "download_format": "PDF / CSV Data Tables",
        "licensing": "Government Open Data License - India (GODL)",
        "notes": "Records human resource availability vs sanctioned posts. Essential for staff resilience baseline."
    },
    "hmis_district_patient_utilization_2022_23": {
        "official_dataset_name": "Health Management Information System (HMIS) - District-Wise Annual Utilization & Service Delivery Factsheets",
        "publisher": "Ministry of Health & Family Welfare (MoHFW) / National Health Mission (NHM)",
        "catalog_url": "https://data.gov.in/keywords/hmis",
        "official_source_url": "https://hmis.mohfw.gov.in/#!/analytical-reports",
        "publication_date": "2023-11-30",
        "last_updated_date": "2024-03-15",
        "temporal_coverage": "2022-2023",
        "spatial_coverage": "District-level across Indian States",
        "granularity": "District monthly / annual facility utilization",
        "provenance_tier": "OFFICIAL_GOVERNMENT",
        "official_columns": [
            "state_name", "district_name", "total_opd_allopathic", "total_opd_ayush",
            "total_ipd_admissions", "institutional_deliveries", "fever_syndromic_surveillance_cases",
            "diarrheal_cases_reported", "acute_respiratory_infections_reported"
        ],
        "data_api_available": True,
        "download_format": "CSV / Excel / OGD Data Portal API",
        "licensing": "Government Open Data License - India (GODL)",
        "notes": "Provides baseline patient footfall and epidemiological disease surge signals for demand forecasting."
    },
    "nlem_essential_medicines_2022": {
        "official_dataset_name": "National List of Essential Medicines of India (NLEM 2022)",
        "publisher": "Ministry of Health & Family Welfare (MoHFW) & CDSCO",
        "catalog_url": "https://cdsco.gov.in/opencms/opencms/en/Drugs/NLEM/",
        "official_source_url": "https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/NLEM_2022.pdf",
        "publication_date": "2022-09-13",
        "last_updated_date": "2022-09-13",
        "temporal_coverage": "2022 - Present",
        "spatial_coverage": "National Formulary",
        "granularity": "384 Essential Medicines across 27 Therapeutic Categories",
        "provenance_tier": "OFFICIAL_GOVERNMENT",
        "official_columns": [
            "medicine_code", "medicine_name", "therapeutic_category", "dosage_form",
            "strength", "route_of_administration", "level_of_healthcare_primary",
            "level_of_healthcare_secondary", "level_of_healthcare_tertiary", "is_emergency_essential"
        ],
        "data_api_available": False,
        "download_format": "Official Gazette Notification / PDF",
        "licensing": "Government Open Data License - India (GODL)",
        "notes": "Standard national master formulary for all public procurement and e-Aushadhi distribution."
    },
    "phc_facility_master_registry": {
        "official_dataset_name": "National Health Facility Directory / Primary Healthcare Registry",
        "publisher": "National Health Authority (NHA) & National Health Portal (NHP)",
        "catalog_url": "https://data.gov.in/keywords/health-facilities",
        "official_source_url": "https://facility.abdm.gov.in/",
        "publication_date": "2023-08-10",
        "last_updated_date": "2024-01-20",
        "temporal_coverage": "2023-2024",
        "spatial_coverage": "Geo-referenced facility directory across States & Districts",
        "granularity": "Individual Facility Node (PHC, CHC, DH)",
        "provenance_tier": "OFFICIAL_GOVERNMENT",
        "official_columns": [
            "facility_id", "facility_name", "state_name", "district_name", "facility_type",
            "latitude", "longitude", "sanctioned_beds", "catchment_population", "is_cold_chain_enabled"
        ],
        "data_api_available": True,
        "download_format": "CSV / GeoJSON",
        "licensing": "Government Open Data License - India (GODL)",
        "notes": "Provides exact GPS coordinates and facility IDs required for geospatial mapping and optimization."
    }
}

def print_discovery_summary():
    print("=" * 80)
    print("SWASTHYA RECORDS - OFFICIAL GOVERNMENT DATASET DISCOVERY REPORT")
    print("=" * 80)
    print(f"Total Official Datasets Cataloged: {len(DATASET_CATALOG)}\n")
    
    for key, meta in DATASET_CATALOG.items():
        print(f"[{key.upper()}]")
        print(f"  Title:        {meta['official_dataset_name']}")
        print(f"  Publisher:    {meta['publisher']}")
        print(f"  Source URL:   {meta['official_source_url']}")
        print(f"  Published:    {meta['publication_date']} | Updated: {meta['last_updated_date']}")
        print(f"  Coverage:     {meta['spatial_coverage']} ({meta['temporal_coverage']})")
        print(f"  Columns ({len(meta['official_columns'])}): {', '.join(meta['official_columns'][:6])}...")
        print(f"  API Available:{meta['data_api_available']} | Format: {meta['download_format']}")
        print(f"  Notes:        {meta['notes']}")
        print("-" * 80)

if __name__ == "__main__":
    print_discovery_summary()
