# SwasthyaGrid Copilot — Operational Tool Schema & Bindings

The SwasthyaGrid Copilot is equipped with 12 deterministic backend tools. Each tool queries live telemetry, inventory databases, Ridge regression forecasting pipelines, or OR-Tools optimization engines.

| Tool # | Function Name | Input Parameters | Output Description |
| :--- | :--- | :--- | :--- |
| **1** | `get_national_summary()` | `user_role`, `assigned_state` | Aggregated facilities, active critical/high warnings, shortages, and active emergencies across India. |
| **2** | `get_state_summary()` | `state: str` | Facility count, critical alerts, state-level bed occupancy and emergency outbreak indicators. |
| **3** | `get_district_summary()` | `district: str` | District-wide bed occupancy %, doctor/nurse presence, and medicine stockout risks. |
| **4** | `get_facility_status()` | `phc_id: str` | Deep telemetry: beds, medical staff, critical medicine DOSA runway, and scheduled in-transit deliveries. |
| **5** | `get_critical_alerts()` | `min_severity: str` | Active early warnings filtered by severity (`CRITICAL`, `HIGH`, `WARNING`). |
| **6** | `get_stockout_risks()` | `state`, `district`, `medicine`, `risk_level`, `time_horizon_days` | Multi-facility inventory risk scan sorted by shortest Days of Stock Available (DOSA). |
| **7** | `get_medicine_status()` | `phc_id: str`, `medicine_id: str` | Granular stock telemetry, consumption rate, reorder point, and days remaining for a medicine. |
| **8** | `get_forecast()` | `phc_id: str`, `resource: str`, `horizon: int` | Multi-day demand predictions with 95% confidence intervals from trained ML models. |
| **9** | `get_redistribution_options()` | `phc_id: str`, `resource: str` | Google OR-Tools MILP source ranking with surplus protection and road transit distances. |
| **10** | `simulate_redistribution()` | `recommendation_id: str` | Isolated Before vs After risk evaluation and inventory impact projection. |
| **11** | `get_emergency_status()` | None | Active disaster, monsoon flood, or outbreak multipliers and affected districts. |
| **12** | `get_resource_pressure()` | None | National supply chain stress ranking for top depleted medicines and overburdened facilities. |
