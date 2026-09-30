# Swasthya Records — Simulation Parameters & Prototype Assumptions

## 1. Scope & Provenance Disclaimer
All parameters documented herein represent engineering assumptions calibrated for the prototype simulation layer. They are explicitly marked as `data_source = "SIMULATED"` and must not be cited as empirical epidemiological statistics of the Government of India.

---

## 2. Parameter Catalog

### A. Patient Utilization & Flow Parameters
| Parameter | Default Value | Rationale / Grounding |
| :--- | :--- | :--- |
| **PHC Base Utilization Rate** | 0.10% of catchment / day | Yields ~70–140 daily OPD visits for rural PHCs (aligned with RHS rural catchment sizes). |
| **CHC Base Utilization Rate** | 0.14% of catchment / day | Yields ~250–500 daily OPD visits for Community Health Centres. |
| **DH Base Utilization Rate** | 0.18% of catchment / day | Yields ~900–2,400 daily visits for District Hospitals. |
| **OPD to IPD Split** | 88% OPD / 12% IPD | Typical rural Indian secondary admission ratio. |
| **Syndromic Fever Ratio** | 8% to 22% of total OPD | Reflects seasonal acute febrile illness patterns in Gangetic and coastal belts. |
| **Average Length of Stay (ALOS)** | 2.4 days | Standard acute hospitalization turnover in primary/secondary care. |

---

### B. Standard Medicine Dispensing Rates (per 100 Patient Footfall)
| Medicine Code | Medicine Name | Base Rate (Units/100 Patients) | Reorder Buffer (Days) | Safety Buffer (Days) |
| :--- | :--- | :--- | :--- | :--- |
| `MED-PCM-500` | Paracetamol 500mg Tablets | 45.0 strips | 7 days | 3 days |
| `MED-PCM-SYR` | Paracetamol Paediatric Syrup | 18.0 bottles | 7 days | 3 days |
| `MED-AMX-500` | Amoxicillin 500mg Capsules | 22.0 strips | 7 days | 3 days |
| `MED-AMC-625` | Amoxicillin + Clavulanic Acid | 14.0 strips | 7 days | 3 days |
| `MED-ORS-SFT` | Oral Rehydration Salts (WHO) | 32.0 sachets | 7 days | 3 days |
| `MED-ZNC-20` | Zinc Sulfate Tablets | 16.0 strips | 7 days | 3 days |
| `MED-AZI-500` | Azithromycin 500mg | 12.0 strips | 7 days | 3 days |
| `MED-CTX-1G` | Ceftriaxone 1g Injection | 6.0 vials | 7 days | 3 days |
| `MED-RAB-VAC` | Anti-Rabies Vaccine | 3.5 vials | 10 days | 5 days |
| `MED-ASV-VIAL`| Anti-Snake Venom Serum | 1.2 vials | 14 days | 7 days |
| `MED-INS-REG` | Human Insulin Regular | 4.0 vials | 10 days | 5 days |
| `MED-MET-500` | Metformin 500mg | 25.0 strips | 7 days | 3 days |
| `MED-OXY-AMP` | Oxytocin 5 IU Injection | 5.0 ampoules | 10 days | 5 days |
| `MED-MGS-50` | Magnesium Sulfate 50% | 2.5 ampoules | 10 days | 5 days |
| `MED-IVF-NS500`| Normal Saline 500ml | 15.0 bottles | 7 days | 3 days |
| `MED-IVF-RL500`| Ringer's Lactate 500ml | 12.0 bottles | 7 days | 3 days |
| `MED-IVF-D5500`| Dextrose 5% 500ml | 8.0 bottles | 7 days | 3 days |
| `MED-ART-60` | Artesunate 60mg Injection | 3.0 vials | 10 days | 5 days |
| `MED-ALB-400` | Albendazole 400mg | 8.0 strips | 7 days | 3 days |
| `MED-IFA-TAB` | Iron & Folic Acid Tablets | 28.0 strips | 7 days | 3 days |

---

### C. Logistics & Transit Assumptions
* **Warehouse Order Lead Time**: Stochastic integer between 4 and 7 days.
* **Batch Replenishment Volume**: 14 days of average daily burn rate.
* **Stock-out Definition**: Closing inventory equal to 0 on any operational date.
