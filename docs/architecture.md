# Swasthya Records — System Architecture

**Product**: **Swasthya Records** (`SwasthyaGrid AI`)  
**Subtitle**: **AI-Powered Health Resource & Supply Chain Resilience Platform**  
**Tagline**: **Predict. Warn. Redistribute. Respond.**  
**Hackathon Track**: Track 3 — Smart Health & Supply Chain Resilience  
**Cloud Infrastructure**: Google Cloud Run (`asia-south1`, Mumbai), Google BigQuery, Vertex AI / Gemini 2.5 Flash  

---

## 1. Executive Summary

Swasthya Records is a national-scale healthcare resource intelligence platform designed to prevent medicine stock-outs, manage patient bed occupancy, and optimize medical logistics across India's Primary Health Centre (PHC) and Community Health Centre (CHC) network.

Rather than acting reactively when inventory reaches zero, the system forecasts demand surges, detects emerging shortages days in advance, and recommends explainable cross-facility resource transfers.

```
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

## 2. Core Architectural Components

### 2.1 Presentation Layer (`frontend/`)
* **Framework**: React 19 + TypeScript bundled with Vite.
* **Styling**: Obsidian Neon palette (dark base `#03010a`, `#080413`, violet primary `#a855f7`, rose accent `#f43f5e`) with high-contrast accessibility and universal `Arial, sans-serif` typography.
* **Geographic Information System (GIS)**: Leaflet.js with custom Sentinel PHC/CHC markers color-coded by stock-out vulnerability.
* **Bilingual Localization**: Seamless English (`en`) and Hindi (`hi`) switching via zero-dependency translation context.
* **Authentication Context**: Role-Based Access Control (`ADMIN`, `STATE_OPERATOR`, `DISTRICT_OPERATOR`) with persistent session guards.

### 2.2 Application & Security Gateway (`backend/app/`)
* **Framework**: FastAPI (Python 3.11/3.14) with Uvicorn ASGI server.
* **Role-Based Scoping (`core/security.py`)**:
  - `ADMIN`: National scope across all 36 States and Union Territories.
  - `STATE_OPERATOR`: Scoped strictly to assigned state code (e.g., `IN-BR` for Bihar); unauthorized cross-state requests are rejected with **HTTP 403 Forbidden**.
  - `DISTRICT_OPERATOR`: Scoped strictly to assigned district code (e.g., `IN-BR-PAT` for Patna).
* **Cost & Abuse Protection (`core/rate_limit.py`)**: Sliding-window rate limiter protecting computationally heavy endpoints (`/copilot/*`, `/redistribution/*`), returning **HTTP 429 Too Many Requests** with `Retry-After`.
* **Structured Observability (`main.py`)**: JSON structured logging middleware generating unique `X-Request-ID` tracing on every request.
* **Liveness & Readiness Probes**:
  - `GET /health`: Fast container orchestrator probe returning `{"status": "ok", "health": "HEALTHY", "code": 200}`.
  - `GET /health/dependencies`: Deep readiness probe checking Database, BigQuery, Gemini AI, and Simulation Engine.

### 2.3 Data Storage & Warehouse Layer
* **Analytical Warehouse (Google BigQuery)**: Dataset `arcadeaiagent.swasthyagrid` storing state-wide facility infrastructure, historical HMIS patient footfall records, and NLEM medicine catalogs.
* **Operational Digital Twin (SQLite Database)**: High-speed relational transactional store maintaining real-time facility inventory, active emergency events, and logged redistribution transfers.
* **In-Memory Predictive Cache**: 60-second TTL cache on ML risk evaluations with automatic invalidation on simulation events, reducing query latency from minutes to **1.1 seconds**.

### 2.4 Artificial Intelligence & Optimization Services
* **Predictive AI (`services/forecasting_service.py`)**: Multi-horizon time-series forecasting (Ridge regression and LightGBM) modeling trend, day-of-week seasonality, and weather/epidemic shocks.
* **Risk Intelligence Engine (`services/risk_engine.py`)**: Computes Days of Stock Available ($DOSA = \frac{\text{Current Stock}}{\text{Projected Daily Demand}}$) and triggers Early Warning Alerts when $DOSA < 3.0$ days.
* **Operations Copilot (`services/copilot_service.py`)**: Grounded Gemini 2.5 Flash assistant answering clinical logistics questions using deterministic backend tools (`get_facility_status`, `calculate_stock_risk`, `recommend_redistribution`).
* **Resource Optimization Engine (`services/optimization_engine.py`)**: Google OR-Tools Mixed-Integer Linear Programming (MILP) solver that finds optimal surplus donor clinics within a 50 km radius without depleting the donor below safe levels.

---

## 3. Data Flow: From Shortage to Solution

1. **Daily Telemetry & Consumption**: Clinics log medicine usage, patient footfall, and bed occupancy.
2. **AI Forecast Update**: Ridge/LightGBM recalculates projected consumption across a 14-day horizon.
3. **Risk Detection**: The Risk Engine flags clinics where projected demand exceeds available stock plus safety buffers.
4. **Early Warning Alert**: If stock is projected to exhaust within 72 hours, an alert is broadcast to district health officers.
5. **AI Reasoning**: Gemini Copilot analyzes the root cause (e.g., flood surge, delayed delivery) and verifies clinical need.
6. **OR-Tools Rebalancing**: The optimizer scans neighboring clinics with surplus stock, calculating transit distance, travel time, and transfer amounts.
7. **Simulate & Approve**: The officer simulates the transfer in the sandbox. Once approved, the recipient's stock runway increases to safe levels.

---

## 4. Disclaimers & Ethics Standards

* **Data Disclaimer**: Swasthya Records is a prototype decision-support platform. Public/government datasets (MoHFW RHS 2022, HMIS, NLEM 2022) are used where available, while operational PHC inventory, demand, staffing and emergency conditions are simulated for demonstration. The prototype does not execute real-world medical logistics.
* **AI Disclaimer**: AI-generated forecasts and recommendations are decision-support outputs and should be reviewed by authorized human operators before operational action.
