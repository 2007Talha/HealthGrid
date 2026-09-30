# Swasthya Records — Hackathon Pitch Deck (12 Slides)

**Product**: **Swasthya Records** (`SwasthyaGrid AI`)  
**Subtitle**: **AI-Powered Health Resource & Supply Chain Resilience Platform**  
**Tagline**: **Predict. Warn. Redistribute. Respond.**  
**Aspect Ratio**: 16:9 Presentation Format  

---

<!-- slide -->
## Slide 1: Title Slide

```text
================================================================================
                                SWASTHYA RECORDS
           AI-Powered Health Resource & Supply Chain Resilience Platform
================================================================================
                    Predict. Warn. Redistribute. Respond.

                          Google GenAI Hackathon 2026
            Track 3: Smart Healthcare & Supply Chain Resilience
               Target Deployment: Google Cloud Run (asia-south1)
================================================================================
```

---

<!-- slide -->
## Slide 2: The Healthcare Vulnerability

### Why Public Health Networks Experience Stock-Outs

```text
  Fragmented Visibility           Late Detection                Preventable Stock-Out
 ┌──────────────────────┐      ┌──────────────────────┐      ┌─────────────────────────┐
 │ Clinic inventories   │ ───► │ Shortage discovered  │ ───► │ Essential medicines     │
 │ tracked on paper or  │      │ only when pharmacy   │      │ reach zero count during │
 │ isolated spreadsheets│      │ shelf is empty       │      │ epidemic surges         │
 └──────────────────────┘      └──────────────────────┘      └─────────────────────────┘
                                                                          │
                                                                          ▼
                                                                  Reactive Logistics
                                                             ┌─────────────────────────┐
                                                             │ Expensive emergency     │
                                                             │ procurement & treatment │
                                                             │ delays for patients     │
                                                             └─────────────────────────┘
```

* **Core Insight**: Healthcare systems don't fail only because resources are unavailable—they fail because decision-makers don't know where shortages are developing until it is too late.

---

<!-- slide -->
## Slide 3: The Solution

### An Intelligent Decision-Support Grid Across Primary Healthcare

```text
  Federated Data            AI Forecasting           Early Warnings          Smart Rebalancing
 ┌──────────────┐          ┌──────────────┐         ┌──────────────┐         ┌─────────────────┐
 │ MoHFW, HMIS, │   ───►   │ 14-day ahead │  ───►   │ Automated    │  ───►   │ Google OR-Tools │
 │ NLEM 2022 &  │          │ burn rate    │         │ mathematical │         │ finds nearest   │
 │ digital twin │          │ calculations │         │ alerts       │         │ helper clinic   │
 └──────────────┘          └──────────────┘         └──────────────┘         └─────────────────┘
                                                                                      │
                                                                                      ▼
                                                                             Human-in-the-Loop
                                                                           ┌───────────────────┐
                                                                           │ Health officer    │
                                                                           │ approves transfer │
                                                                           │ via simulation    │
                                                                           └───────────────────┘
```

---

<!-- slide -->
## Slide 4: System Architecture

```text
                     PUBLIC & OPERATIONAL DATA FOUNDATION
            MoHFW RHS 2022 • HMIS 2022-23 • CDSCO NLEM 2022 • Census
                                       │
                                       ▼
                       DATA WAREHOUSE & DIGITAL TWIN
               Google BigQuery (OLAP) • SQLite (Real-time Twin)
                                       │
              ┌────────────────────────┼────────────────────────┐
              ▼                        ▼                        ▼
       PREDICTIVE AI             RISK ENGINE             GEMINI COPILOT
     Ridge + LightGBM          Days of Stock           Grounded Reasoning
     Demand Forecasts         Available (DOSA)         & Tool Execution
              │                        │                        │
              └────────────────────────┼────────────────────────┘
                                       │
                                       ▼
                         RESOURCE REDISTRIBUTION
                Google OR-Tools Mixed-Integer Programming
                                       │
                                       ▼
                     NATIONAL RESILIENCE COMMAND CENTER
                React 19 • Leaflet GIS • Bilingual (EN / HI)
```

---

<!-- slide -->
## Slide 5: The AI & Optimization Framework

| Pillar | Technology | Functional Role in Swasthya Records |
| :--- | :--- | :--- |
| **1. Predictive AI** | Ridge Regression & LightGBM | Projects 7 and 14-day forward medicine consumption taking into account seasonality and surge shocks. |
| **2. Risk Engine** | Probabilistic Thresholds | Calculates Days of Stock Available ($DOSA = \frac{\text{Stock}}{\text{Demand}}$) to detect breaches before inventory hits zero. |
| **3. Operations Copilot** | Gemini 2.5 Flash on Vertex AI | Grounded natural language assistant answering logistics queries using deterministic backend database tools. |
| **4. Optimization** | Google OR-Tools (CBC MILP) | Solves cross-facility redistribution under strict donor safety thresholds and distance boundaries. |
| **5. Voice Accessibility** | Web Speech API | Provides voice recognition and speech readout in English and Hindi for frontline health workers. |

---

<!-- slide -->
## Slide 6: End-to-End Judge Demonstration

```text
 1. Baseline View        2. Flood Shock        3. AI Spike           4. Early Warning
┌──────────────────┐    ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│ 33 Clinics mapped│───►│ Patna floods hit│──►│ Usage jumps     │──►│ Patna PHC runs  │
│ 20 Medicines     │    │ +40% OPD demand │   │ to 185 units/day│   │ out in 1.4 days │
└──────────────────┘    └─────────────────┘   └─────────────────┘   └─────────────────┘
                                                                             │
                                                                             ▼
 7. Risk Eliminated      6. Rebalancing        5. Gemini AI Explanation
┌──────────────────┐    ┌─────────────────┐   ┌─────────────────┐
│ Stock runway     │◄───│ OR-Tools finds  │◄──│ Explains surge  │
│ restored to 14.2d│    │ Danapur surplus │   │ using verified  │
│ Zero stock-outs  │    │ 200 units @18km │   │ database tools  │
└──────────────────┘    └─────────────────┘   └─────────────────┘
```

* **Live Demo**: Ready at [http://localhost:5173/demo](http://localhost:5173/demo) with a 1-click deterministic flow.

---

## Slide 7: Designed for India Scale

### Multi-Tier Administrative Architecture

```text
                                  NATIONAL LEVEL
                       Ministry of Health & Family Welfare
                     Macro supply chain visibility across India
                                       │
                                       ▼
                                  STATE LEVEL
                      36 States & Union Territories (e.g. IN-BR)
                      State Nodal Officers & Allocation Hubs
                                       │
                                       ▼
                                 DISTRICT LEVEL
                     District Chief Medical Officers (CMO)
                     Cross-facility rebalancing within 50 km
                                       │
                                       ▼
                                  LOCAL LEVEL
                     Primary & Community Health Centres (PHCs / CHCs)
                     Daily consumption, bed occupancy, doctor check-in
```

* Strict **Role-Based Access Control (RBAC)** ensures officers see only their authorized administrative jurisdictions.

---

<!-- slide -->
## Slide 8: Data Integrity & Provenance

### Absolute Transparency Between Real Government Data and Simulation

```text
┌───────────────────────────────────────────────┬───────────────────────────────────────────────┐
│ OFFICIAL PUBLIC GOVERNMENT DATA               │ PROTOTYPE OPERATIONAL SIMULATION              │
├───────────────────────────────────────────────┼───────────────────────────────────────────────┤
│ • Rural Health Statistics (RHS 2021-22):      │ • Daily Medicine Inventory & Dispensation:    │
│   Official facility registry, bed count, GPS. │   Simulated daily consumption telemetry.      │
│ • Health Management Information System (HMIS):│ • Active Emergency Flooding Multipliers:      │
│   Outpatient footfall and inpatient baselines.│   Simulated +40% surge in Patna District.     │
│ • National List of Essential Medicines (NLEM):│ • Digital Twin Intervention Sandbox:          │
│   384 essential formulations & unit pack sizes│   Simulates redistribution before execution.  │
└───────────────────────────────────────────────┴───────────────────────────────────────────────┘
```

* **No Hallucinations**: Zero fabricated facility names or non-existent medicine codes.

---

<!-- slide -->
## Slide 9: Google Cloud Infrastructure

* **Google Cloud Run**: Serverless container orchestration with auto-scaling, health probes, and non-root security.
* **Google BigQuery**: Enterprise analytical warehouse housing public healthcare datasets and time-series history.
* **Vertex AI / Gemini 2.5 Flash**: Grounded operational reasoning with deterministic function calling.
* **Google OR-Tools**: Industrial-grade linear programming solver for cross-district vehicle routing.
* **Google Artifact Registry**: Secure Docker container storage in `asia-south1` (Mumbai).

---

<!-- slide -->
## Slide 10: Measurable Operational Capabilities

* **Predict Shortages Earlier**: Flags emerging stock depletion up to **72 hours in advance** instead of discovering empty shelves.
* **Prioritize High-Risk Facilities**: Automatically categorizes clinics by urgency ($DOSA < 3\text{ days}$).
* **Identify Safe Nearby Surplus**: Finds donor facilities with excess stock without causing a secondary shortage.
* **Simulate Interventions Safely**: Allows health directors to test transfers in a risk-free digital twin.
* **Explain Decisions Transparently**: Gives medical officers plain-English and Hindi rationales backed by math.

---

<!-- slide -->
## Slide 11: Enterprise Security & Compliance

* **Least-Privilege Scoping**: State operators cannot view or manipulate records from other states (**403 Forbidden**).
* **Sliding-Window Rate Limiting**: Protects expensive Gemini and optimization endpoints (**429 Too Many Requests**).
* **Structured JSON Cloud Logging**: Unique `X-Request-ID` attached to all requests for complete audit traceability.
* **Zero Secret Exposure**: 100% environment-driven configuration with zero hardcoded API keys.
* **Ethical AI Protocol**: Clear disclaimers indicating decision-support role with mandatory human operator sign-off.

---

<!-- slide -->
## Slide 12: Closing

```text
================================================================================
                     FROM REACTIVE HEALTHCARE LOGISTICS
                         TO PREDICTIVE RESILIENCE.

                               SWASTHYA RECORDS
                     Predict. Warn. Redistribute. Respond.
================================================================================
```

> *"Swasthya Records turns fragmented healthcare-resource signals into an early-warning and response system—predicting demand, identifying shortages, finding safe redistribution opportunities, and giving decision-makers an explainable AI copilot."*

* **GitHub Repository**: `https://github.com/2007Talha/HealthGrid.git`  
* **GCP Project**: `arcadeaiagent`  
* **Team**: Swasthya Records Engineering Team
