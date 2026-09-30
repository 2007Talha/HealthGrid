# Swasthya Records — Phase 4: Cross-District Resource Redistribution Intelligence

## 1. Executive Summary

In public healthcare supply chains across India, localized surges and logistics delays often cause critical primary healthcare facilities (PHCs) to face impending medicine stock-outs. Simultaneously, neighboring facilities in the same or adjacent districts may possess substantial stock above their emergency safety reserves.

**Phase 4** of Swasthya Records implements an intelligent, constraint-aware decision-support engine that:
1. Automatically scans and quantifies healthcare resource shortages across PHCs.
2. Identifies nearby candidate donor facilities with safe, non-jeopardizing surplus.
3. Formulates and solves a Mixed-Integer Linear Programming (MILP) optimization problem using **Google OR-Tools**.
4. Computes calibrated road-network routing matrices (distance, transit time, speed limits).
5. Provides a completely reversible simulation sandbox (`PROPOSED` $\to$ `SIMULATED` $\to$ `RESET`) to evaluate the before/after operational impact on stock coverage and risk reduction without modifying underlying government records.
6. Synthesizes bilingual (English/Hindi) audit explanations powered by Gemini grounded strictly in the solver's mathematical outputs.

> **Operational Guardrail**: The system provides decision-support recommendations only and does NOT automatically dispatch real-world medical shipments without human authorization.

---

## 2. Core Architecture & Pipeline

```
+-----------------------------------------------------------------------------+
|                            PHASE 4 ARCHITECTURE                             |
+-----------------------------------------------------------------------------+
|                                                                             |
|  [PHC Inventory & Forecast] -> [Risk Engine (DOSA < 3d / CRITICAL)]        |
|                                       |                                     |
|                                       v                                     |
|                      [Shortage Identification Scanner]                      |
|                                       |                                     |
|                                       v                                     |
|                      [Candidate Source Discovery Engine]                    |
|                        - Geo-Radius Filter (< 300 km)                       |
|                        - Surplus Protection: I_s - max(SS_s, 10*D_s) > 0    |
|                        - Ranked by Multi-Objective Score                    |
|                                       |                                     |
|                                       v                                     |
|                      [Google OR-Tools MILP Solver]                          |
|                        - Minimize Distance + Fragmentation Penalties        |
|                        - Preserves Safety Reserves                          |
|                        - Multi-Source Consolidation                         |
|                                       |                                     |
|             +-------------------------+-------------------------+           |
|             |                                                   |           |
|             v                                                   v           |
|  [Reversible Simulation Sandbox]              [Grounded Gemini Explanations]|
|   - State: PROPOSED -> SIMULATED               - English & Hindi Audit Trail|
|   - Recalculates Risk Before/After             - Strictly Grounded in Solver|
|   - Non-destructive Simulation Buffer          - Anti-Hallucination Guard   |
|             |                                                   |           |
|             +-------------------------+-------------------------+           |
|                                       v                                     |
|                  [BigQuery Layer: arcadeaiagent.swasthyagrid]               |
|                   - redistribution_routes (1,056 rows)                      |
|                   - redistribution_recommendations (8 rows)                 |
|                   - redistribution_candidates (363 rows)                    |
|                   - redistribution_simulations (8 rows)                     |
+-----------------------------------------------------------------------------+
```

---

## 3. Mathematical Formulation

### 3.1 Protected Reserve & Usable Surplus
For any candidate source facility $s$ with current inventory $I_s$, safety stock threshold $\text{SafetyStock}_s$, and daily consumption $\bar{D}_s$:

$$\text{ProtectedReserve}_s = \max\left(\text{SafetyStock}_s, \text{ProtectionWindow} \times \bar{D}_s\right)$$

where $\text{ProtectionWindow} = 10\text{ days}$.

The safe transferable surplus is strictly defined as:

$$\text{Surplus}_s = \max\left(0, I_s - \text{ProtectedReserve}_s\right)$$

### 3.2 Net Deficit at Destination
For destination facility $d$ with target buffer $\text{TargetStock}_d = \text{SafetyStock}_d + 7 \times \bar{D}_d$:

$$\text{NetNeed}_d = \max\left(0, \text{TargetStock}_d - I_d - \text{IncomingImmediate}\right)$$

### 3.3 Multi-Objective MILP Optimization
$$\min \sum_{s \in S} \left( c_{\text{dist}} \cdot d_{sd} \cdot x_{sd} + c_{\text{fixed}} \cdot y_s \right)$$

Subject to:
1. **Supply Limit**: $x_{sd} \le \text{Surplus}_s \cdot y_s \quad \forall s \in S$
2. **Demand Fulfillment**: $\sum_{s \in S} x_{sd} = \min\left(\text{NetNeed}_d, \sum_{s \in S} \text{Surplus}_s\right)$
3. **Source Cap**: $\sum_{s \in S} y_s \le K \quad (K = 2 \text{ or } 3)$
4. **Binary & Integer**: $y_s \in \{0, 1\}, \quad x_{sd} \in \mathbb{Z}_{\ge 0}$

---

## 4. Reversible Simulation Workflow

To allow public health officers to explore "what-if" scenarios:
- **Baseline**: Original official inventory and historical records remain untouched.
- **Simulation Layer**: Transfers are simulated in an active operational state layer.
- **Risk Transition**: Destination Days of Stock Available (DOSA) increases (e.g. $1.8\text{d} \to 8.5\text{d}$), lowering risk from $\text{CRITICAL} \to \text{LOW}$.
- **One-Click Reset**: State is seamlessly rolled back to pre-simulation parameters with full audit verification.
