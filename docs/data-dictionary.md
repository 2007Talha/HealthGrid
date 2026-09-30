# Swasthya Records — Data Dictionary & Entity Definitions

This document details every table, column, data type, business key, and description across the Swasthya Records data architecture.

---

## 1. Table: `facility_master`
* **Table Description**: Master registry of public healthcare facilities (PHCs, CHCs, District Hospitals) with official administrative and geographic metadata.
* **Provenance Category**: OFFICIAL_GOVERNMENT (NHA / NHP Facility Registry)
* **BigQuery Clustering**: `state_code`, `district_code`, `facility_type`

| Column Name | Data Type | Mode | Primary/Foreign Key | Description | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `facility_id` | STRING | REQUIRED | PRIMARY KEY | Unique national facility identifier | `PHC-BR-PAT-001` |
| `facility_name` | STRING | REQUIRED | - | Official facility title | `PHC Bakhtiyarpur` |
| `facility_type` | STRING | REQUIRED | - | Classification (`PHC`, `CHC`, `District Hospital`) | `PHC` |
| `state_name` | STRING | REQUIRED | - | State name | `Bihar` |
| `state_code` | STRING | REQUIRED | - | Standard ISO state code | `IN-BR` |
| `district_name` | STRING | REQUIRED | - | District name | `Patna` |
| `district_code` | STRING | REQUIRED | - | Standard district code | `BR-PATNA` |
| `latitude` | FLOAT | REQUIRED | - | GPS latitude coordinate | `25.4600` |
| `longitude` | FLOAT | REQUIRED | - | GPS longitude coordinate | `85.5300` |
| `sanctioned_beds` | INTEGER | REQUIRED | - | Official bed capacity from RHS | `6` |
| `catchment_population` | INTEGER | NULLABLE | - | Estimated catchment population served | `125000` |
| `sanctioned_doctors` | INTEGER | REQUIRED | - | Sanctioned Medical Officers in position | `2` |
| `sanctioned_nurses` | INTEGER | REQUIRED | - | Sanctioned Staff Nurses | `4` |
| `is_cold_chain_enabled`| BOOLEAN | REQUIRED | - | Functional ILR / Deep Freezer available | `true` |
| `accessibility_tier` | STRING | REQUIRED | - | Geographic tier (`Urban`, `Rural Plain`, `Hilly`) | `Rural Plain` |
| `data_source` | STRING | REQUIRED | - | Provenance identifier (`OFFICIAL_GOVERNMENT`) | `OFFICIAL_GOVERNMENT` |
| `provenance_tier` | STRING | REQUIRED | - | Source dataset code | `NHA_FACILITY_REGISTRY` |
| `source_url` | STRING | REQUIRED | - | Official source URL | `https://facility.abdm.gov.in/` |
| `retrieved_at` | TIMESTAMP | REQUIRED | - | Ingestion timestamp | `2026-08-23T20:55:00Z` |

---

## 2. Table: `facility_infrastructure`
* **Table Description**: State-level aggregated infrastructure from Rural Health Statistics (Health Dynamics of India 2022-23).
* **Provenance Category**: OFFICIAL_GOVERNMENT (MoHFW RHS)
* **BigQuery Clustering**: `state_code`

| Column Name | Data Type | Mode | Description |
| :--- | :--- | :--- | :--- |
| `state_name` | STRING | REQUIRED | Indian State / UT name |
| `state_code` | STRING | REQUIRED | ISO 3166-2:IN state code |
| `sub_centres_functioning` | INTEGER | REQUIRED | Total operational Sub-Centres |
| `phcs_functioning` | INTEGER | REQUIRED | Total operational Primary Health Centres |
| `chcs_functioning` | INTEGER | REQUIRED | Total operational Community Health Centres |
| `sub_divisional_hospitals` | INTEGER | REQUIRED | Total operational Sub-Divisional Hospitals |
| `district_hospitals` | INTEGER | REQUIRED | Total operational District Hospitals |
| `total_phc_beds` | INTEGER | REQUIRED | Total sanctioned beds across all PHCs in state |
| `total_chc_beds` | INTEGER | REQUIRED | Total sanctioned beds across all CHCs in state |
| `total_dh_beds` | INTEGER | REQUIRED | Total sanctioned beds across all DHs in state |
| `phcs_with_regular_power_supply` | INTEGER | NULLABLE | Count of PHCs with 24x7 regular power |
| `phcs_with_water_supply` | INTEGER | NULLABLE | Count of PHCs with continuous piped water |
| `phcs_with_all_weather_motorable_road` | INTEGER | NULLABLE | Count of PHCs with all-weather road access |
| `phc_electrification_rate_pct` | FLOAT | NULLABLE | Computed % of electrified PHCs |
| `phc_all_weather_road_access_pct` | FLOAT | NULLABLE | Computed % of road-accessible PHCs |
| `data_source` | STRING | REQUIRED | `OFFICIAL_GOVERNMENT` |
| `provenance_tier` | STRING | REQUIRED | `RHS_2022_23` |

---

## 3. Table: `personnel`
* **Table Description**: Healthcare human resources, sanctioned vs in-position staff, vacancies and shortfalls.
* **Provenance Category**: OFFICIAL_GOVERNMENT (MoHFW RHS)
* **BigQuery Clustering**: `state_code`

| Column Name | Data Type | Mode | Description |
| :--- | :--- | :--- | :--- |
| `state_name` | STRING | REQUIRED | State Name |
| `state_code` | STRING | REQUIRED | State Code |
| `doctors_at_phcs_sanctioned` | INTEGER | REQUIRED | Sanctioned allopathic medical officers at PHCs |
| `doctors_at_phcs_in_position`| INTEGER | REQUIRED | Medical officers physically in position |
| `doctors_at_phcs_vacant` | INTEGER | REQUIRED | Vacant doctor posts |
| `specialists_at_chcs_sanctioned`| INTEGER | REQUIRED | Sanctioned specialists at CHCs (Surgeon, OBGYN, etc.) |
| `specialists_at_chcs_in_position`| INTEGER | REQUIRED | In-position specialists at CHCs |
| `specialists_at_chcs_vacant` | INTEGER | REQUIRED | Vacant specialist posts |
| `nursing_staff_sanctioned` | INTEGER | REQUIRED | Sanctioned Staff Nurse positions |
| `nursing_staff_in_position`| INTEGER | REQUIRED | In-position Staff Nurses |
| `anm_sanctioned` | INTEGER | REQUIRED | Sanctioned Auxiliary Nurse Midwives |
| `anm_in_position` | INTEGER | REQUIRED | In-position Auxiliary Nurse Midwives |
| `pharmacists_sanctioned` | INTEGER | REQUIRED | Sanctioned Pharmacists |
| `pharmacists_in_position`| INTEGER | REQUIRED | In-position Pharmacists |
| `doctor_vacancy_rate_pct` | FLOAT | NULLABLE | Computed % doctor vacancies at PHCs |
| `specialist_vacancy_rate_pct`| FLOAT | NULLABLE | Computed % specialist vacancies at CHCs |

---

## 4. Table: `patient_utilization`
* **Table Description**: Historical patient footfall, OPD/IPD admissions, and epidemiological syndromic surveillance indicators.
* **Provenance Category**: OFFICIAL_GOVERNMENT (MoHFW HMIS)
* **BigQuery Clustering**: `state_code`, `district_code`

| Column Name | Data Type | Mode | Description |
| :--- | :--- | :--- | :--- |
| `state_name` | STRING | REQUIRED | State Name |
| `state_code` | STRING | REQUIRED | State Code |
| `district_name` | STRING | REQUIRED | District Name |
| `district_code` | STRING | REQUIRED | Standard District Code |
| `total_opd_allopathic` | INTEGER | REQUIRED | Annual Allopathic OPD attendance |
| `total_opd_ayush` | INTEGER | REQUIRED | Annual AYUSH OPD attendance |
| `total_ipd_admissions` | INTEGER | REQUIRED | Annual In-Patient admissions |
| `institutional_deliveries` | INTEGER | REQUIRED | Institutional childbirth deliveries |
| `fever_syndromic_surveillance_cases` | INTEGER | REQUIRED | Fever / Dengue / Malaria surveillance cases |
| `diarrheal_cases_reported` | INTEGER | REQUIRED | Acute Diarrheal Disease (ADD) cases |
| `acute_respiratory_infections_reported` | INTEGER | REQUIRED | Acute Respiratory Infections (ARI) cases |
| `total_opd_combined` | INTEGER | REQUIRED | Combined OPD volume |
| `fever_burden_ratio` | FLOAT | NULLABLE | Ratio of fever cases to total OPD volume |
| `ipd_to_opd_ratio` | FLOAT | NULLABLE | Ratio of hospitalizations to outpatient visits |

---

## 5. Table: `medicine_reference`
* **Table Description**: Standard National Essential Medicine Formulary from NLEM 2022.
* **Provenance Category**: OFFICIAL_GOVERNMENT (CDSCO / NLEM 2022)
* **BigQuery Clustering**: `therapeutic_category`, `is_emergency_essential`

| Column Name | Data Type | Mode | Description |
| :--- | :--- | :--- | :--- |
| `medicine_code` | STRING | REQUIRED (PK) | Standard Drug Identifier (e.g. `MED-PCM-500`) |
| `medicine_name` | STRING | REQUIRED | Generic Drug Name |
| `therapeutic_category` | STRING | REQUIRED | Classification (`Analgesic`, `Antibacterial`, `Vaccine`) |
| `dosage_form` | STRING | REQUIRED | Form (`Tablet`, `Injection`, `Syrup`, `Sachet`) |
| `strength` | STRING | REQUIRED | Dosage strength |
| `route_of_administration` | STRING | REQUIRED | `Oral`, `IV Infusion`, `IM`, `Subcutaneous` |
| `level_of_healthcare_primary` | BOOLEAN | REQUIRED | Indicated for Primary Healthcare (PHC) |
| `level_of_healthcare_secondary`| BOOLEAN | REQUIRED | Indicated for Secondary Healthcare (CHC) |
| `level_of_healthcare_tertiary` | BOOLEAN | REQUIRED | Indicated for Tertiary Healthcare (DH) |
| `is_emergency_essential` | BOOLEAN | REQUIRED | Flag for high-priority life-saving redistribution |
| `unit_packaging` | STRING | REQUIRED | Standard packaging unit |
| `standard_shelf_life_months` | INTEGER | REQUIRED | Shelf life in months |

---

## 6. Table: `phc_operational_status` (Simulated Telemetry Schema)
* **Table Description**: Real-time simulated telemetry for high-resolution stock, bed occupancy, doctor/nurse daily attendance, and delivery ETAs.
* **Provenance Category**: **SIMULATED** (Explicit Prototype Operational Telemetry Layer)
* **BigQuery Partitioning**: `DATE(timestamp)` | **Clustering**: `phc_id`, `medicine_id`

| Column Name | Data Type | Mode | Description |
| :--- | :--- | :--- | :--- |
| `phc_id` | STRING | REQUIRED | Facility Reference (FK -> `facility_master.facility_id`) |
| `timestamp` | TIMESTAMP | REQUIRED | Telemetry timestamp |
| `medicine_id` | STRING | REQUIRED | Medicine Reference (FK -> `medicine_reference.medicine_code`) |
| `current_stock` | INTEGER | REQUIRED | Units on hand |
| `daily_consumption` | INTEGER | REQUIRED | Units dispensed past 24 hours |
| `beds_total` | INTEGER | REQUIRED | Functional bed capacity |
| `beds_occupied` | INTEGER | REQUIRED | Current occupied beds |
| `doctors_scheduled` | INTEGER | REQUIRED | Doctors on duty roster |
| `doctors_present` | INTEGER | REQUIRED | Doctors physically clocked in |
| `nurses_scheduled` | INTEGER | REQUIRED | Nurses on duty roster |
| `nurses_present` | INTEGER | REQUIRED | Nurses physically clocked in |
| `patient_footfall` | INTEGER | REQUIRED | Total daily patient visits |
| `medicine_delivery_eta` | TIMESTAMP | NULLABLE | Next warehouse delivery ETA |
| `emergency_status` | STRING | REQUIRED | `NORMAL`, `OUTBREAK_ALERT`, `FLOOD_ALERT`, `SHORTAGE_CRITICAL` |
| `data_source` | STRING | REQUIRED | Explicitly set to `"SIMULATED"` |
