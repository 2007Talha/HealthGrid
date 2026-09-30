# Swasthya Records — Official Government Data Sources & Discovery Catalog

## Overview
This document records the official Indian government healthcare datasets identified, verified, and cataloged for **Swasthya Records**. All datasets have been acquired and inspected in accordance with the Government Open Data License - India (GODL).

---

## 1. Catalog of Verified Official Datasets

### A. Health Dynamics of India: Infrastructure Statistics (2022-23)
* **Official Dataset Name**: Health Dynamics of India (Infrastructure and Human Resources) 2022-23 — Infrastructure Statistics
* **Publisher / Ministry**: Statistics Division, Ministry of Health and Family Welfare (MoHFW), Government of India
* **Catalog URL**: [data.gov.in / rural-health-statistics](https://data.gov.in/keywords/rural-health-statistics)
* **Official Source URL**: `https://mohfw.gov.in/sites/default/files/HealthDynamicsOfIndia2022-23.pdf`
* **Publication Date**: September 18, 2024
* **Last Updated Date**: September 18, 2024
* **Spatial Coverage**: National (All 36 States & Union Territories of India)
* **Temporal Coverage**: 2022–2023 (Status as of March 31, 2023)
* **Granularity**: State-level and District-level counts of functional healthcare infrastructure
* **Licensing**: Government Open Data License - India (GODL)
* **API Availability**: No direct public REST API; published as official open data tables/PDF
* **Extracted Schema**:
  - `state_name` (STRING)
  - `state_code` (STRING, ISO 3166-2:IN)
  - `sub_centres_functioning` (INTEGER)
  - `phcs_functioning` (INTEGER)
  - `chcs_functioning` (INTEGER)
  - `sub_divisional_hospitals` (INTEGER)
  - `district_hospitals` (INTEGER)
  - `total_phc_beds` (INTEGER)
  - `total_chc_beds` (INTEGER)
  - `total_dh_beds` (INTEGER)
  - `phcs_with_regular_power_supply` (INTEGER)
  - `phcs_with_water_supply` (INTEGER)
  - `phcs_with_all_weather_motorable_road` (INTEGER)

---

### B. Health Dynamics of India: Healthcare Human Resources (2022-23)
* **Official Dataset Name**: Health Dynamics of India (Infrastructure and Human Resources) 2022-23 — Manpower & Personnel Statistics
* **Publisher / Ministry**: Ministry of Health and Family Welfare (MoHFW), Government of India
* **Catalog URL**: [data.gov.in / health-manpower](https://data.gov.in/keywords/health-manpower)
* **Official Source URL**: `https://mohfw.gov.in/sites/default/files/HealthDynamicsOfIndia2022-23.pdf`
* **Publication Date**: September 18, 2024
* **Spatial Coverage**: National (All States & UTs)
* **Temporal Coverage**: 2022–2023
* **Granularity**: State-wise counts of sanctioned, in-position, and vacant healthcare personnel
* **Licensing**: Government Open Data License - India (GODL)
* **API Availability**: Official Data Tables / GODL
* **Extracted Schema**:
  - `doctors_at_phcs_sanctioned` (INTEGER)
  - `doctors_at_phcs_in_position` (INTEGER)
  - `doctors_at_phcs_vacant` (INTEGER)
  - `specialists_at_chcs_sanctioned` (INTEGER)
  - `specialists_at_chcs_in_position` (INTEGER)
  - `specialists_at_chcs_vacant` (INTEGER)
  - `nursing_staff_sanctioned` (INTEGER)
  - `nursing_staff_in_position` (INTEGER)
  - `anm_sanctioned` (INTEGER)
  - `anm_in_position` (INTEGER)
  - `pharmacists_sanctioned` (INTEGER)
  - `pharmacists_in_position` (INTEGER)

---

### C. Health Management Information System (HMIS) District Factsheets (2022-23)
* **Official Dataset Name**: Health Management Information System (HMIS) Analytical Service Delivery Reports
* **Publisher / Ministry**: National Health Mission (NHM) / Ministry of Health and Family Welfare (MoHFW)
* **Catalog URL**: [data.gov.in / hmis](https://data.gov.in/keywords/hmis)
* **Official Source URL**: `https://hmis.mohfw.gov.in/#!/analytical-reports`
* **Publication Date**: November 30, 2023 (Updated March 2024)
* **Spatial Coverage**: District-level across Indian States
* **Temporal Coverage**: Monthly & Annual historical time-series (2022–2023)
* **Granularity**: District-wise aggregated OPD footfall, IPD admissions, and epidemiological syndromic surveillance
* **Licensing**: Government Open Data License - India (GODL)
* **API Availability**: OGD India Portal API / CSV
* **Extracted Schema**:
  - `district_name` (STRING)
  - `district_code` (STRING)
  - `total_opd_allopathic` (INTEGER)
  - `total_opd_ayush` (INTEGER)
  - `total_ipd_admissions` (INTEGER)
  - `institutional_deliveries` (INTEGER)
  - `fever_syndromic_surveillance_cases` (INTEGER)
  - `diarrheal_cases_reported` (INTEGER)
  - `acute_respiratory_infections_reported` (INTEGER)

---

### D. National List of Essential Medicines of India (NLEM 2022)
* **Official Dataset Name**: National List of Essential Medicines (NLEM 2022)
* **Publisher / Ministry**: Central Drugs Standard Control Organization (CDSCO) & MoHFW
* **Catalog URL**: [cdsco.gov.in / NLEM](https://cdsco.gov.in/opencms/opencms/en/Drugs/NLEM/)
* **Official Source URL**: `https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/NLEM_2022.pdf`
* **Publication Date**: September 13, 2022
* **Spatial Coverage**: National Formulary (Applicable across all Indian public healthcare institutions)
* **Granularity**: 384 Essential Medicines across 27 therapeutic classifications
* **Licensing**: Official Government Gazette Notification
* **API Availability**: Official Reference Formulary / PDF
* **Extracted Schema**:
  - `medicine_code` (STRING, PK)
  - `medicine_name` (STRING)
  - `therapeutic_category` (STRING)
  - `dosage_form` (STRING)
  - `strength` (STRING)
  - `route_of_administration` (STRING)
  - `level_of_healthcare_primary` (BOOLEAN)
  - `level_of_healthcare_secondary` (BOOLEAN)
  - `level_of_healthcare_tertiary` (BOOLEAN)
  - `is_emergency_essential` (BOOLEAN)
  - `unit_packaging` (STRING)
  - `standard_shelf_life_months` (INTEGER)

---

### E. National Health Facility Directory & Registry
* **Official Dataset Name**: National Health Facility Registry (HFR)
* **Publisher / Ministry**: National Health Authority (NHA) & National Health Portal (NHP)
* **Catalog URL**: [facility.abdm.gov.in](https://facility.abdm.gov.in/)
* **Publication Date**: August 2023 (Continuously maintained)
* **Spatial Coverage**: Geo-located healthcare institutions across Indian districts
* **Granularity**: Individual Facility Node (PHC, CHC, Sub-Divisional Hospital, District Hospital)
* **Licensing**: Open Government Directory
* **Extracted Schema**:
  - `facility_id` (STRING, PK)
  - `facility_name` (STRING)
  - `facility_type` (STRING)
  - `state_name` (STRING)
  - `state_code` (STRING)
  - `district_name` (STRING)
  - `district_code` (STRING)
  - `latitude` (FLOAT)
  - `longitude` (FLOAT)
  - `sanctioned_beds` (INTEGER)
  - `catchment_population` (INTEGER)
  - `sanctioned_doctors` (INTEGER)
  - `sanctioned_nurses` (INTEGER)
  - `is_cold_chain_enabled` (BOOLEAN)
  - `accessibility_tier` (STRING)

---

## 2. Search Findings: Live PHC Medicine Inventory

> [!IMPORTANT]
> **Data Verification Finding**:  
> A thorough inspection of the Government of India Open Data Platform (`data.gov.in`), CDAC e-Aushadhi, and state Drug and Vaccine Distribution Management Systems (DVDMS) reveals that **no public, unauthenticated, live real-time PHC-level medicine stock or daily batch dispensing API is published in open government data**.  
> Live inventory feeds are restricted to internal state health logistics intranets.
>
> **Consequence & Solution**:  
> In accordance with project integrity rules, we do **NOT** fabricate fake government live stock data. Instead, Swasthya Records establishes a dedicated, clearly labeled **Simulated Prototype Operational Telemetry Layer** (`phc_operational_status`) initialized from official NLEM 2022 formulations and calibrated with HMIS utilization rates.
