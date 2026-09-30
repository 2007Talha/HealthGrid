# Swasthya Records — Early Warning Alert Engine & Gemini Explainer

## 1. Engine Architecture
The Early Warning Engine integrates signals from ML forecasts, physical stock levels, bed telemetry, staffing rosters, and shipment tracking to produce standardized, actionable warnings.

---

## 2. Alert Taxonomy

| Alert Type | Trigger Condition | Default Severity |
| :--- | :--- | :--- |
| `MEDICINE_STOCKOUT_RISK` | $\text{DOSA} < 2.0\text{d}$ or stock exhausted | `CRITICAL` |
| `RAPID_DEMAND_SURGE` | Anomaly $Z_t \ge 2.8$ (+50% deviation) | `HIGH` |
| `BED_CAPACITY_RISK` | Inpatient occupancy $\ge 90\%$ (overflow $\ge 100\%$) | `HIGH` / `CRITICAL` |
| `STAFF_SHORTAGE_RISK` | Medical Officer attendance deficit during surge | `HIGH` |
| `DELAYED_DELIVERY` | In-transit shipment past estimated arrival date | `WARNING` |
| `EMERGENCY_OUTBREAK_SURGE` | Active district outbreak scenario declaration | `CRITICAL` |

---

## 3. Evidence Payload Contract
Every alert is strictly grounded on empirical data:
```json
{
  "alert_id": "ALT-MED-4F7A91B2",
  "severity": "CRITICAL",
  "alert_type": "MEDICINE_STOCKOUT_RISK",
  "facility_id": "PHC-BR-PAT-001",
  "facility_name": "PHC Bakhtiyarpur",
  "resource_id": "MED-PCM-500",
  "resource_name": "Paracetamol",
  "evidence_summary": "Current Physical Stock: 412 units | Predicted 7-Day Burn Rate: 342.5 units/day | Safety Stock Threshold: 850 units | DOSA: 1.2 days | Projected stock-out in ~1.2 days (2026-08-25).",
  "projected_impact": "Immediate stock-out expected in ~1.2 days (DOSA: 1.2d). High risk of treatment failure for acute patients.",
  "recommended_next_step": "Authorize emergency redistribution transfer from nearest surplus facility in district (e.g. PHC Danapur).",
  "created_at": "2026-08-23T15:45:00Z",
  "status": "ACTIVE"
}
```

---

## 4. Grounded Gemini Explainer Integration
* **Endpoint**: `POST /api/v1/ai/explain-alert`
* **Role of Gemini**: Synthesizes clear, multilingual (English & Hindi) executive explanations for district health officers based **strictly on the verified evidence payload**.
* **Safety & Anti-Hallucination Guardrails**:
  1. If payload is absent $\implies$ Returns *"There is insufficient evidence to determine this reliably."*
  2. Prohibited from inventing stock numbers or clinical diagnosis.
