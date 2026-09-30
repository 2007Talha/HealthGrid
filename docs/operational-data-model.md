# Swasthya Records — Unified Operational Data Model

## 1. Overview & Architectural Principles
The Swasthya Records Operational Data Model provides a high-resolution, unified schema representing daily and real-time facility telemetry across Indian Primary Health Centres (PHCs), Community Health Centres (CHCs), and District Hospitals.

```
+----------------------------------------------------------------------------------------------------+
|                                SWASTHYA UNIFIED OPERATIONAL SCHEMA                                 |
+----------------------------------------------------------------------------------------------------+
| Master Dimensions (Official Base) | Operational Telemetry Stream (Simulated Layer)                 |
|   - facility_id                   |   - patient_footfall (OPD, IPD, Syndromic Fever)               |
|   - state_name, state_code        |   - beds_total, beds_occupied, beds_available, occupancy_%     |
|   - district_name, district_code  |   - doctors_scheduled, doctors_present, doctor_shortage_flag   |
|   - facility_type, coordinates    |   - nurses_scheduled, nurses_present, nurse_shortage_flag      |
|   - medicine_code, medicine_name  |   - opening_stock, received_qty, daily_consumption, closing    |
|   - therapeutic_category          |   - reorder_level, safety_stock, days_of_stock_available (DOSA)|
|                                   |   - medicine_delivery_eta, delivery_status                     |
|                                   |   - emergency_status (NORMAL, SURGE_ALERT, CRITICAL_SURGE)     |
|                                   |   - data_source = "SIMULATED"                                  |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Table Schemas & Entity Specifications

### Table 1: `phc_operational_daily`
* **Purpose**: Tracks daily patient footfall, bed occupancy rates, doctor/nurse rostered attendance, and facility emergency status.
* **Granularity**: 1 record per facility per calendar day.
* **Storage**: BigQuery table `arcadeaiagent.swasthyagrid.phc_operational_daily` & CSV `data/processed/simulated/phc_operational_daily.csv`.

| Field Name | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `phc_id` | STRING | NOT NULL | Facility Identifier (FK -> `facility_master.facility_id`) |
| `facility_name` | STRING | NOT NULL | Official Facility Name |
| `state_name` | STRING | NOT NULL | State Name (e.g., Bihar, Uttar Pradesh) |
| `district_name` | STRING | NOT NULL | District Name (e.g., Patna, Varanasi) |
| `district_code` | STRING | NOT NULL | Standard District Code |
| `record_date` | DATE | NOT NULL | Operational Date (YYYY-MM-DD) |
| `timestamp` | TIMESTAMP | NOT NULL | Daily closing timestamp (20:00:00 IST) |
| `patient_footfall` | INT64 | $\ge 0$ | Total registered patient footfall |
| `opd_patients` | INT64 | $\ge 0$ | Out-Patient Department consults |
| `ipd_patients` | INT64 | $\ge 0$ | In-Patient admissions |
| `fever_syndromic_cases` | INT64 | $\ge 0$ | Fever / Dengue / Malaria syndromic surveillance cases |
| `beds_total` | INT64 | $\ge 0$ | Total functional beds (from RHS sanctioned capacity) |
| `beds_occupied` | INT64 | $\le \text{beds\_total}$ | Inpatient occupied beds |
| `beds_available` | INT64 | $\ge 0$ | Unoccupied available beds |
| `bed_occupancy_rate_pct`| FLOAT64 | $0.0 - 100.0$ | $\frac{\text{beds\_occupied}}{\text{beds\_total}} \times 100$ |
| `doctors_scheduled` | INT64 | $\ge 0$ | Rostered medical officers |
| `doctors_present` | INT64 | $\le \text{scheduled}$| Physically clocked-in doctors |
| `nurses_scheduled` | INT64 | $\ge 0$ | Rostered nursing staff |
| `nurses_present` | INT64 | $\le \text{scheduled}$| Physically clocked-in nurses |
| `doctor_shortage_flag` | BOOL | - | True if doctor shortage during surge |
| `nurse_shortage_flag` | BOOL | - | True if nurse presence $< 70\%$ |
| `emergency_status` | STRING | - | `NORMAL`, `SURGE_ALERT`, `CRITICAL_SURGE`, `BED_OVERFLOW` |
| `data_source` | STRING | - | Explicitly `"SIMULATED"` |

---

### Table 2: `medicine_inventory_daily`
* **Purpose**: Tracks itemized daily stock balance, consumption, restock deliveries, safety thresholds, and Days of Stock Available (DOSA).
* **Granularity**: 1 record per facility per medicine per calendar day (33 facilities $\times$ 20 medicines = 660 records/day).
* **Storage**: BigQuery table `arcadeaiagent.swasthyagrid.medicine_inventory_daily`.

| Field Name | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `phc_id` | STRING | NOT NULL | Facility Identifier |
| `facility_name` | STRING | NOT NULL | Facility Name |
| `medicine_code` | STRING | NOT NULL | Standard Drug Code (FK -> `medicine_reference.medicine_code`) |
| `medicine_name` | STRING | NOT NULL | Generic Medicine Name |
| `therapeutic_category` | STRING | NOT NULL | NLEM Classification |
| `record_date` | DATE | NOT NULL | Operational Date |
| `opening_stock` | INT64 | $\ge 0$ | Stock on hand at start of day |
| `received_quantity` | INT64 | $\ge 0$ | Incoming delivery units received today |
| `daily_consumption` | INT64 | $\ge 0$ | Units dispensed to patients today |
| `closing_stock` | INT64 | $\ge 0$ | $\max(0, \text{opening} + \text{received} - \text{consumed})$ |
| `reorder_level` | INT64 | $\ge 0$ | Threshold triggering automated batch orders |
| `safety_stock` | INT64 | $\ge 0$ | Minimum required buffer (3-day average burn) |
| `days_of_stock_available`| FLOAT64| $\ge 0.0$ | $\frac{\text{closing\_stock}}{\text{daily\_consumption}}$ |
| `stock_out_occurred` | BOOL | - | True if closing stock reaches 0 |
| `data_source` | STRING | - | Explicitly `"SIMULATED"` |

---

### Table 3: `medicine_deliveries`
* **Purpose**: Tracks supply-chain replenishment orders and inter-facility transfers from dispatch to destination receipt.
* **Storage**: BigQuery table `arcadeaiagent.swasthyagrid.medicine_deliveries`.

| Field Name | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `delivery_id` | STRING | NOT NULL (PK) | Unique Shipment Identifier (`DEL-XXXXXXXX`) |
| `phc_id` | STRING | NOT NULL | Destination Facility Identifier |
| `facility_name` | STRING | NOT NULL | Destination Facility Name |
| `medicine_code` | STRING | NOT NULL | Drug Identifier |
| `medicine_name` | STRING | NOT NULL | Medicine Title |
| `quantity` | INT64 | $> 0$ | Batch shipment quantity in standard units |
| `dispatch_date` | DATE | NOT NULL | Date shipment left warehouse / source facility |
| `expected_arrival_date`| DATE | NOT NULL | Scheduled delivery ETA |
| `actual_arrival_date` | DATE | NULLABLE | Actual delivery completion date |
| `status` | STRING | NOT NULL | `SCHEDULED`, `IN_TRANSIT`, `DELIVERED`, `DELAYED`, `CANCELLED` |
| `data_source` | STRING | - | Explicitly `"SIMULATED"` |
