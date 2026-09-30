# Swasthya Records

### **AI-Powered Health Resource & Supply Chain Resilience Platform**

> **Tagline**: *Predict. Warn. Redistribute. Respond.*  
> **Google Cloud GenAI Hackathon 2026 — Track 3: Smart Health & Supply Chain Resilience**  
> **GCP Project ID**: `arcadeaiagent` | **Region**: `asia-south1` (Mumbai)  
> **GitHub Repository**: [https://github.com/2007Talha/HealthGrid.git](https://github.com/2007Talha/HealthGrid.git)  

---

## One-Line Overview

> **SwasthyaGrid AI is an India-scale AI platform that forecasts healthcare resource demand, detects emerging shortages, and recommends cross-district redistribution before critical stock-outs occur.**

---

## Executive Summary

> **SwasthyaGrid AI provides a unified view of medicine stocks, patient demand, beds, staffing and health-resource risks across India's PHC network. Gemini and predictive models transform operational data into early warnings and explainable redistribution recommendations, helping decision-makers respond before shortages become critical.**

---

## 1. The Healthcare Problem

Across India's vast public healthcare network—spanning over 30,000 Primary Health Centres (PHCs) and Community Health Centres (CHCs)—critical medicine stock-outs and bed saturation often occur unpredictably. Seasonal disease outbreaks (such as post-monsoon dengue, malaria, and flood-borne diarrheal episodes) trigger localized demand surges of $300\%\text{--}500\%$.

Simultaneously, neighboring districts frequently possess substantial unutilized surplus inventory. Because supply-chain records remain siloed and administrative redistributions require days of coordination, preventable patient mortalities and emergency stock-outs persist.

```text
Fragmented Visibility ──► Late Detection ──► Stock-Outs ──► Reactive Logistics
```

---

## 2. The Solution: Swasthya Records

Swasthya Records provides an automated intelligence and decision-support layer:

1. **Predicts**: Multi-horizon AI forecasting (Ridge Regression and LightGBM) predicts demand surges across 7-day and 14-day horizons before shelves empty.
2. **Warns**: An automated Risk Intelligence Engine classifies facilities into vulnerability tiers using Days of Stock Available ($DOSA = \frac{\text{Stock}}{\text{Demand}}$) and generates early warnings 72 hours in advance.
3. **Redistributes**: A Mixed-Integer Linear Programming (MILP) solver powered by **Google OR-Tools** computes minimum-cost, capacity-constrained cross-district rebalancing routes with strict source safety stock safeguards.
4. **Responds**: **Swasthya Records AI Assistant**, powered by **Gemini 2.5 Flash**, provides voice-enabled, grounded operational intelligence and interactive What-If simulation sandboxing for healthcare directors.

---

## 3. Core Features

* **National Command Dashboard**: Real-time geospatial telemetry mapping 33 sentinel facilities across Bihar, Uttar Pradesh, and Maharashtra with Leaflet GIS.
* **AI Demand & Stock Forecasting**: Multi-horizon projections factoring in outpatient footfall (OPD), seasonality, and emergency multipliers.
* **Google OR-Tools Supply Rebalancing**: Mathematical optimization solving the multi-source, multi-destination transfer problem under road distance and cold-chain constraints.
* **Gemini 2.5 Flash Operations Copilot**: Natural language assistant utilizing 10+ deterministic backend tools for auditable, hallucination-free decision support.
* **What-If Practice Sandbox**: Shadow simulation environment evaluating hypothetical demand spikes (+30%), transit delays (+3 days), and emergency shipments before execution.
* **Bilingual Localization (English / हिन्दी)**: Instant language switching across all navigation, KPI cards, tables, chart labels, and alerts.
* **Role-Based Access Control (RBAC)**: Role-scoped views for `ADMIN` (National Director), `STATE_OPERATOR` (State Director), and `DISTRICT_OPERATOR` (District Nodal Officer).
* **1-Click Guided Demo Flow**: 7-step self-guided tour illustrating baseline telemetry $\to$ disaster surge $\to$ forecast spike $\to$ alert $\to$ Copilot explanation $\to$ OR-Tools rebalancing $\to$ risk reduction.
* **Data Sources & Provenance Page**: Dedicated `/data-sources` transparency route documenting all government data foundations and simulation boundaries.

---

## 4. System Architecture

```text
                           INTERNET / USER BROWSER
                                      │
                                      ▼
                        Google Cloud Run (asia-south1)
                     Swasthya Records Web Application
                                      │
           ┌──────────────────────────┼──────────────────────────┐
           ▼                          ▼                          ▼
    React 19 + TypeScript        FastAPI Gateway          Gemini 2.5 Flash
    (Tailwind + Leaflet GIS)     (REST + RBAC + Audit)    (Operations Copilot)
           │                          │                          │
           │                          ▼                          │
           │            ┌─────────────┴─────────────┐            │
           │            ▼                           ▼            │
           │      Google BigQuery               SQLite DB        │
           │    (Government DW OLAP)          (Operational Twin) │
           │            │                           │            │
           │            ▼                           ▼            │
           │     Demand Forecast              OR-Tools MILP      │
           │    (Ridge / LightGBM)           (Supply Rebalancer) │
           │            │                           │            │
           └────────────┴─────────────┬─────────────┴────────────┘
                                      ▼
                        Official Data Provenance
               MoHFW RHS 2022 • HMIS 2022-23 • NLEM 2022
```

---

## 5. AI Approach & Methodology

Swasthya Records combines four distinct AI pillars:

1. **Predictive AI**: Multi-horizon Ridge Regression and LightGBM forecasting trained on seasonal consumption curves, OPD visits, and weather/epidemic shocks.
2. **Risk Intelligence**: Grounded mathematical calculation of Days of Stock Available ($DOSA$). Flags shortages when $DOSA < 3.0\text{ days}$.
3. **Generative AI (Gemini 2.5 Flash)**: Acts as an explainable operations copilot. All responses are strictly grounded in deterministic backend Python tool outputs (`get_facility_status`, `calculate_stock_risk`, `recommend_redistribution`).
4. **Combinatorial Optimization (Google OR-Tools)**: Mixed-Integer Linear Programming solver computing optimal donor-recipient transfer pairs while enforcing a 7-day donor safety buffer and a 50 km transit radius.

---

## 6. Data Integrity & Provenance

Swasthya Records maintains strict separation between official government data and prototype operational simulations:

| Dataset | Publisher | Source Type | Coverage | Usage in Swasthya Records |
| :--- | :--- | :--- | :--- | :--- |
| **Rural Health Statistics (RHS) 2022** | MoHFW, Govt of India | Official Public | 36 States & UTs | Facility registry, bed counts, geographic coordinates |
| **HMIS 2022-2023** | NHM, MoHFW | Official Public | District aggregates | Patient footfall and bed occupancy baselines |
| **National List of Essential Medicines (NLEM 2022)** | Dept of Pharmaceuticals / CDSCO | Government Formulary | 384 formulations | 20 tracked essential therapeutic medicines & pack sizes |
| **Census of India** | Ministry of Home Affairs | Official Demographics | National | Population distributions and transit distances |
| **Operational Digital Twin** | Swasthya Records Simulator | Prototype Simulation | 33 Sentinel Clinics | Daily inventory consumption and emergency flood surges |

---

## 7. Google Cloud Technologies

* **Google Cloud Run**: Serverless container hosting with non-root security context and auto-scaling.
* **Google BigQuery**: Analytical data warehouse hosting official public government records (`arcadeaiagent.swasthyagrid`).
* **Vertex AI / Gemini 2.5 Flash**: Natural language operations copilot and What-If scenario explanation.
* **Google OR-Tools**: Industrial-grade Mixed-Integer Linear Programming solver for logistics optimization.
* **Artifact Registry**: Secure Docker container repository in region `asia-south1`.

---

## 8. Local Setup & Installation

### Prerequisites
* Python 3.11+
* Node.js 18+ and npm
* Git

### Step 1: Clone Repository
```bash
git clone https://github.com/2007Talha/HealthGrid.git
cd HealthGrid
```

### Step 2: Backend Setup
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

### Step 3: Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Visit the application at `http://localhost:5173/`.

---

## 9. Environment Variables

Create a `.env` file in the root directory (see `.env.example`):

```env
GCP_PROJECT_ID=arcadeaiagent
GCP_REGION=asia-south1
BIGQUERY_DATASET=arcadeaiagent.swasthyagrid
GEMINI_MODEL=gemini-2.5-flash
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
RATE_LIMIT_PER_MINUTE=60
ENVIRONMENT=development
```

---

## 10. Cloud Run Production Deployment

Execute the automated Cloud Run deployment script:

```bash
chmod +x scripts/deploy_cloud_run.sh
./scripts/deploy_cloud_run.sh
```

Or deploy locally using Docker Compose:
```bash
docker-compose up --build
```

---

## 11. Judge Demonstration Walkthrough (3 Minutes)

Experience the full resilience lifecycle in 7 steps at `/demo`:

1. **Baseline Operations**: 33 sentinel facilities operate normally across Bihar, UP, and Maharashtra.
2. **Trigger Emergency**: Inject a Monsoon Flood Surge in Patna District (+40% demand).
3. **Forecast Spike**: Predictive models detect accelerated burn rate for ORS and Paracetamol.
4. **Early Warning Alert**: The system alerts officers that Patna Sadar will exhaust stock in 1.4 days.
5. **Ask Gemini Copilot**: Gemini analyzes the root cause using verified database records.
6. **OR-Tools Rebalancing**: The optimizer identifies Danapur Clinic as a safe donor (200 units, 18 km).
7. **Simulate & Approve**: The officer approves the transfer; stock runway restores to 14.2 days.

---

## 12. Security & Compliance

* **Role-Based Access Control**: Strict least-privilege scoping (`ADMIN`, `STATE_OPERATOR`, `DISTRICT_OPERATOR`). Unauthorized cross-state queries return **HTTP 403 Forbidden**.
* **Sliding-Window Rate Limiting**: Protects expensive endpoints with **HTTP 429 Too Many Requests**.
* **Structured Observability**: Logs all requests in JSON with `X-Request-ID` tracing without logging credentials.
* **Anti-Hallucination Guardrail**: Regex registry validation rejects non-existent facility queries.
* **Privacy by Design**: No patient Personally Identifiable Information (PII) is collected or stored.

---

## 13. Limitations & Roadmap

* **Live Inventory Integration**: Currently uses simulated operational telemetry because rural PHCs do not yet expose public real-time dispensing APIs. Production deployment will integrate with state e-Aushadhi / DVDMS systems via ABDM standards.
* **Cold-Chain Sensor Telemetry**: Simulated temperature curves. Future phases will ingest live IoT cold-box telemetry.
* **Road Conditions**: Travel times are computed using Haversine distance and regional transit averages. Live integration with Google Maps Distance Matrix API is supported.

---

## 14. Disclaimers

### Data Disclaimer
> **Swasthya Records is a prototype decision-support platform. Public/government datasets are used where available, while operational PHC inventory, demand, staffing and emergency conditions may be simulated for demonstration. The prototype does not execute real-world medical logistics.**

### AI Disclaimer
> **AI-generated forecasts and recommendations are decision-support outputs and should be reviewed by authorized human operators before operational action.**

---

## 15. Final Judge Message

> *"Swasthya Records turns fragmented healthcare-resource signals into an early-warning and response system—predicting demand, identifying shortages, finding safe redistribution opportunities, and giving decision-makers an explainable AI copilot."*
