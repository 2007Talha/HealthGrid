# Swasthya Records — Data Provenance & Architectural Boundary

## 1. Core Principle of Provenance
Swasthya Records upholds absolute transparency. In a critical public health and emergency supply chain application, mixing real government baselines with simulated prototype feeds without clear demarcation is unacceptable.

```
+----------------------------------------------------------------------------------------------------+
|                                    DATA PROVENANCE ARCHITECTURE                                    |
+----------------------------------------------------------------------------------------------------+
| TIER 1: OFFICIAL GOVERNMENT BASELINE LAYER                                                         |
|   - Provenance Tag: data_source = "OFFICIAL_GOVERNMENT"                                            |
|   - Authorities: Ministry of Health & Family Welfare (MoHFW), CDSCO, NHA, National Health Mission   |
|   - Publications: Health Dynamics of India (RHS 2022-23), HMIS Analytical Reports, NLEM 2022       |
|   - Scope: Geospatial facility coordinates, sanctioned beds, sanctioned doctor/nurse ratios,       |
|            state/district hierarchies, official essential medicine formulary.                      |
|   - Guarantee: 100% Unmodified, Ground-Truth Indian Public Healthcare Infrastructure Data.         |
+----------------------------------------------------------------------------------------------------+
| TIER 2: SIMULATED PROTOTYPE OPERATIONAL TELEMETRY LAYER                                            |
|   - Provenance Tag: data_source = "SIMULATED"                                                      |
|   - Justification: Open government portals do not publish minute-by-minute medicine stock counts   |
|                    or live doctor biometric clock-ins due to intranet access controls.             |
|   - Generation Engine: Calibrated stochastic simulation driven by RHS capacity weights,            |
|                        HMIS disease seasonal multipliers, and standard NLEM dosages.               |
|   - User Interface: Every simulated metric carries explicit [SIMULATED TELEMETRY] badges.          |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Ingested Dataset Provenance Matrix

| Table Name | Source Authority | Official Source Reference | Ingestion Method | Provenance Tag |
| :--- | :--- | :--- | :--- | :--- |
| `facility_master` | NHA / ABDM / NHP | `https://facility.abdm.gov.in/` | Cleaned CSV / BigQuery | `OFFICIAL_GOVERNMENT` (`NHA_FACILITY_REGISTRY`) |
| `facility_infrastructure` | MoHFW Statistics Division | `https://mohfw.gov.in/` (RHS 2022-23) | Cleaned CSV / BigQuery | `OFFICIAL_GOVERNMENT` (`RHS_2022_23`) |
| `personnel` | MoHFW Statistics Division | `https://mohfw.gov.in/` (RHS 2022-23) | Cleaned CSV / BigQuery | `OFFICIAL_GOVERNMENT` (`RHS_2022_23`) |
| `patient_utilization` | MoHFW / NHM | `https://hmis.mohfw.gov.in/` | Cleaned CSV / BigQuery | `OFFICIAL_GOVERNMENT` (`HMIS_2022_23`) |
| `medicine_reference` | CDSCO / MoHFW | `https://cdsco.gov.in/` (NLEM 2022) | Cleaned CSV / BigQuery | `OFFICIAL_GOVERNMENT` (`NLEM_2022`) |
| `phc_operational_status`| Swasthya Prototype Engine | Mathematical Stochastic Simulator | BigQuery Stream / Partition | `SIMULATED` (`PROTOTYPE_OPERATIONAL_FEED`) |

---

## 3. BigQuery Storage Details
* **Google Cloud Project**: `arcadeaiagent`
* **BigQuery Dataset**: `arcadeaiagent.swasthyagrid`
* **Region / Location**: `asia-south1` (Mumbai, India)
* **Encryption**: Google-managed encryption at rest & in transit
* **Audit Logging**: Cloud Audit Logs enabled for all BigQuery query and load jobs
