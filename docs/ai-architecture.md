# Swasthya Records — Artificial Intelligence & Optimization Architecture

**Product**: **Swasthya Records** (`SwasthyaGrid AI`)  
**Subtitle**: **AI-Powered Health Resource & Supply Chain Resilience Platform**  
**Tagline**: **Predict. Warn. Redistribute. Respond.**  

---

## 1. Overview

Swasthya Records employs a layered artificial intelligence architecture combining **predictive machine learning**, **probabilistic risk calculation**, **deterministic combinatorial optimization**, and **grounded generative reasoning**.

Each AI component is bound by strict ethical and computational constraints:
* Models never fabricate medical records or hallucinate facility inventories.
* Generative responses from Gemini query deterministic backend APIs.
* Optimization models enforce strict non-depletion constraints on donor facilities.

---

## 2. The Four AI Pillars

```
┌────────────────────────────────────────────────────────────────────────┐
│                        1. PREDICTIVE AI                                │
│  Demand Forecasting: Ridge Regression + LightGBM Multi-Horizon Models  │
│  - Captures 7-day seasonality, patient footfall, and flood surge shocks │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      2. RISK INTELLIGENCE                              │
│  Stock-Out Prediction & Early Warning Engine                           │
│  - Days of Stock Available (DOSA), safety buffer breach thresholds     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     3. GROUNDED GEMINI COPILOT                         │
│  Gemini 2.5 Flash with Deterministic Function Calling Tools            │
│  - Queries facility status, explains root cause, evaluates scenarios   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     4. RESOURCE OPTIMIZATION                           │
│  Google OR-Tools Mixed-Integer Linear Programming (MILP)               │
│  - Optimal transfer routing, minimum transit time, donor safety buffer │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Pillar Specifications

### Pillar 1: Predictive Demand Forecasting
* **Algorithm**: Regularized Ridge Regression with LightGBM gradient-boosted decision trees.
* **Input Features**:
  - Historical 90-day medicine consumption time series.
  - Day-of-week seasonality (capturing typical rural clinic peak days).
  - Outpatient footfall (OPD) baseline from HMIS.
  - Emergency demand multipliers (e.g., $+40\%$ surge during monsoon flooding).
* **Forecast Horizon**: 7-day and 14-day forward projections.
* **Output**: Projected daily unit consumption rate ($\hat{D}_{t}$) with $80\%$ and $95\%$ prediction intervals.

### Pillar 2: Stock-Out Risk Intelligence Engine
* **Formula**:
  $$\text{DOSA} = \frac{\text{Current Usable Stock}}{\hat{D}_{\text{daily average}}}$$
* **Thresholds**:
  - **CRITICAL / URGENT**: $\text{DOSA} < 3.0\text{ days}$ or stock exhausted within lead time.
  - **HIGH RISK**: $3.0 \le \text{DOSA} < 7.0\text{ days}$.
  - **WATCHLIST**: $7.0 \le \text{DOSA} < 14.0\text{ days}$.
  - **HEALTHY**: $\text{DOSA} \ge 14.0\text{ days}$.
* **Confidence Metric**: Grounded in historical forecast error ($RMSE$) and variance of lead times.

### Pillar 3: Grounded Operations Copilot (Gemini 2.5 Flash)
* **Model**: Gemini 2.5 Flash via Vertex AI SDK (with grounded mock fallback).
* **Tool Calling Capabilities**:
  1. `get_facility_status(facility_id)`: Fetches real-time inventory, beds, and staff.
  2. `calculate_stock_risk(facility_id, medicine_code)`: Retrieves DOSA and shortage risk.
  3. `recommend_redistribution(facility_id, medicine_code, days_buffer)`: Executes OR-Tools rebalancing.
  4. `simulate_transfer(source_id, dest_id, quantity)`: Runs shadow transfer without altering live records.
* **Hallucination Safeguard**: Regex parsing checks facility IDs against registry (e.g., querying `PHC-999999` returns an explicit "Facility ID not found in registry" message).

### Pillar 4: Cross-District Redistribution Optimization (Google OR-Tools)
* **Solver**: CBC / SCIP Mixed-Integer Linear Programming (MILP).
* **Objective Function**:
  $$\min \sum_{i \in \text{Donors}} \sum_{j \in \text{Recipients}} \left( c_{ij} \cdot x_{ij} + \lambda \cdot d_{ij} \right)$$
  Where $x_{ij}$ is the transfer quantity, $c_{ij}$ is the logistics cost per unit, $d_{ij}$ is road transit distance in kilometers, and $\lambda$ is an urgency weight.
* **Hard Constraints**:
  1. **Donor Non-Depletion**: No donor clinic may send stock if doing so drops its own $\text{DOSA} < 7\text{ days}$.
  2. **Recipient Need Cap**: Recipient receives only enough stock to restore $\text{DOSA}$ to a 14-day safe buffer.
  3. **Transit Radius**: Donors are prioritized within a 50 km radius to ensure delivery within 2–4 hours.

---

## 4. Multilingual & Voice Interface

* **Multilingual Translation**: Bilingual dictionary layer (`en.json` and `hi.json`) covering all UI elements, metric names, and action prompts.
* **Voice Recognition**: Browser Web Speech API (`webkitSpeechRecognition`) supporting natural English and Hindi queries.
* **Voice Synthesis**: SpeechSynthesis API with clean voice readout of Gemini Copilot recommendations.

---

## 5. AI Ethics & Human-in-the-Loop Protocol

1. **Decision Support Only**: AI outputs are recommendations. Real-world dispatch requires review and sign-off by a qualified human health official.
2. **Deterministic Sandbox**: What-If simulation experiments are fully isolated from baseline database records.
3. **Audit Trail**: Every AI query, prompt, tool invocation, and recommendation is logged with timestamp, user ID, and latency in structured JSON.
