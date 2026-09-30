-- ============================================================================
-- SWASTHYA RECORDS: BigQuery DDL Architecture
-- GCP Project: arcadeaiagent
-- Dataset: swasthyagrid
-- Description: Ground-truth official Indian public health infrastructure & operational telemetry
-- ============================================================================

-- 1. Facility Master Registry (Official Government Base)
CREATE TABLE IF NOT EXISTS `arcadeaiagent.swasthyagrid.facility_master` (
  facility_id STRING NOT NULL OPTIONS(description="Unique Health Facility Identifier (PK)"),
  facility_name STRING NOT NULL OPTIONS(description="Official Name of the Facility"),
  facility_type STRING NOT NULL OPTIONS(description="PHC, CHC, Sub-Divisional Hospital, District Hospital"),
  state_name STRING NOT NULL OPTIONS(description="Indian State Name"),
  state_code STRING NOT NULL OPTIONS(description="ISO State Code (e.g. IN-UP, IN-BR)"),
  district_name STRING NOT NULL OPTIONS(description="District Name"),
  district_code STRING NOT NULL OPTIONS(description="Standard District Code"),
  latitude FLOAT64 NOT NULL OPTIONS(description="Geographic Latitude"),
  longitude FLOAT64 NOT NULL OPTIONS(description="Geographic Longitude"),
  sanctioned_beds INT64 NOT NULL OPTIONS(description="Sanctioned bed capacity from RHS"),
  catchment_population INT64 OPTIONS(description="Estimated population served"),
  sanctioned_doctors INT64 NOT NULL OPTIONS(description="Sanctioned Medical Officers in position"),
  sanctioned_nurses INT64 NOT NULL OPTIONS(description="Sanctioned Staff Nurses"),
  is_cold_chain_enabled BOOL NOT NULL OPTIONS(description="Presence of functional vaccine/insulin cold chain"),
  accessibility_tier STRING NOT NULL OPTIONS(description="Urban, Peri-Urban, Rural Plain, Hilly/Remote, Tribal"),
  data_source STRING NOT NULL OPTIONS(description="OFFICIAL_GOVERNMENT"),
  provenance_tier STRING NOT NULL OPTIONS(description="NHA_FACILITY_REGISTRY"),
  source_url STRING NOT NULL OPTIONS(description="Official Source URL"),
  retrieved_at TIMESTAMP NOT NULL OPTIONS(description="Data retrieval timestamp")
)
CLUSTER BY state_code, district_code, facility_type;

-- 2. Facility Infrastructure Statistics (Official MoHFW RHS)
CREATE TABLE IF NOT EXISTS `arcadeaiagent.swasthyagrid.facility_infrastructure` (
  state_name STRING NOT NULL,
  state_code STRING NOT NULL,
  sub_centres_functioning INT64 NOT NULL,
  phcs_functioning INT64 NOT NULL,
  chcs_functioning INT64 NOT NULL,
  sub_divisional_hospitals INT64 NOT NULL,
  district_hospitals INT64 NOT NULL,
  total_phc_beds INT64 NOT NULL,
  total_chc_beds INT64 NOT NULL,
  total_dh_beds INT64 NOT NULL,
  phcs_with_regular_power_supply INT64,
  phcs_with_water_supply INT64,
  phcs_with_all_weather_motorable_road INT64,
  phc_electrification_rate_pct FLOAT64,
  phc_all_weather_road_access_pct FLOAT64,
  data_source STRING NOT NULL,
  provenance_tier STRING NOT NULL,
  source_url STRING NOT NULL,
  retrieved_at TIMESTAMP NOT NULL
)
CLUSTER BY state_code;

-- 3. Healthcare Personnel & Human Resources (Official MoHFW RHS)
CREATE TABLE IF NOT EXISTS `arcadeaiagent.swasthyagrid.personnel` (
  state_name STRING NOT NULL,
  state_code STRING NOT NULL,
  doctors_at_phcs_sanctioned INT64 NOT NULL,
  doctors_at_phcs_in_position INT64 NOT NULL,
  doctors_at_phcs_vacant INT64 NOT NULL,
  specialists_at_chcs_sanctioned INT64 NOT NULL,
  specialists_at_chcs_in_position INT64 NOT NULL,
  specialists_at_chcs_vacant INT64 NOT NULL,
  nursing_staff_sanctioned INT64 NOT NULL,
  nursing_staff_in_position INT64 NOT NULL,
  anm_sanctioned INT64 NOT NULL,
  anm_in_position INT64 NOT NULL,
  pharmacists_sanctioned INT64 NOT NULL,
  pharmacists_in_position INT64 NOT NULL,
  doctor_vacancy_rate_pct FLOAT64,
  specialist_vacancy_rate_pct FLOAT64,
  data_source STRING NOT NULL,
  provenance_tier STRING NOT NULL,
  source_url STRING NOT NULL,
  retrieved_at TIMESTAMP NOT NULL
)
CLUSTER BY state_code;

-- 4. Historical Patient Utilization (Official MoHFW HMIS)
CREATE TABLE IF NOT EXISTS `arcadeaiagent.swasthyagrid.patient_utilization` (
  state_name STRING NOT NULL,
  state_code STRING NOT NULL,
  district_name STRING NOT NULL,
  district_code STRING NOT NULL,
  total_opd_allopathic INT64 NOT NULL,
  total_opd_ayush INT64 NOT NULL,
  total_ipd_admissions INT64 NOT NULL,
  institutional_deliveries INT64 NOT NULL,
  fever_syndromic_surveillance_cases INT64 NOT NULL,
  diarrheal_cases_reported INT64 NOT NULL,
  acute_respiratory_infections_reported INT64 NOT NULL,
  total_opd_combined INT64 NOT NULL,
  fever_burden_ratio FLOAT64,
  ipd_to_opd_ratio FLOAT64,
  data_source STRING NOT NULL,
  provenance_tier STRING NOT NULL,
  source_url STRING NOT NULL,
  retrieved_at TIMESTAMP NOT NULL
)
CLUSTER BY state_code, district_code;

-- 5. National Essential Medicine Formulary (Official CDSCO NLEM 2022)
CREATE TABLE IF NOT EXISTS `arcadeaiagent.swasthyagrid.medicine_reference` (
  medicine_code STRING NOT NULL OPTIONS(description="Standard Drug Code (PK)"),
  medicine_name STRING NOT NULL OPTIONS(description="Generic Name"),
  therapeutic_category STRING NOT NULL,
  dosage_form STRING NOT NULL,
  strength STRING NOT NULL,
  route_of_administration STRING NOT NULL,
  level_of_healthcare_primary BOOL NOT NULL,
  level_of_healthcare_secondary BOOL NOT NULL,
  level_of_healthcare_tertiary BOOL NOT NULL,
  is_emergency_essential BOOL NOT NULL,
  unit_packaging STRING NOT NULL,
  standard_shelf_life_months INT64 NOT NULL,
  data_source STRING NOT NULL,
  provenance_tier STRING NOT NULL,
  source_url STRING NOT NULL,
  retrieved_at TIMESTAMP NOT NULL
)
CLUSTER BY therapeutic_category, is_emergency_essential;

-- 6. PHC Operational Status (SIMULATED TELEMETRY LAYER)
-- Note: Explicitly segregated from Official Base records.
CREATE TABLE IF NOT EXISTS `arcadeaiagent.swasthyagrid.phc_operational_status` (
  phc_id STRING NOT NULL OPTIONS(description="FK -> facility_master.facility_id"),
  timestamp TIMESTAMP NOT NULL OPTIONS(description="Telemetry Timestamp"),
  medicine_id STRING NOT NULL OPTIONS(description="FK -> medicine_reference.medicine_code"),
  current_stock INT64 NOT NULL OPTIONS(description="Units available"),
  daily_consumption INT64 NOT NULL OPTIONS(description="Units consumed past 24h"),
  beds_total INT64 NOT NULL,
  beds_occupied INT64 NOT NULL,
  doctors_scheduled INT64 NOT NULL,
  doctors_present INT64 NOT NULL,
  nurses_scheduled INT64 NOT NULL,
  nurses_present INT64 NOT NULL,
  patient_footfall INT64 NOT NULL,
  medicine_delivery_eta TIMESTAMP,
  emergency_status STRING NOT NULL,
  data_source STRING NOT NULL OPTIONS(description="SIMULATED - Explicit prototype operational feed")
)
PARTITION BY DATE(timestamp)
CLUSTER BY phc_id, medicine_id;
