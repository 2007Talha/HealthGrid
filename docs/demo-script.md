# Swasthya Records — Judge Presentation & Demo Script

**Product**: **Swasthya Records** (`SwasthyaGrid AI`)  
**Subtitle**: **AI-Powered Health Resource & Supply Chain Resilience Platform**  
**Tagline**: **Predict. Warn. Redistribute. Respond.**  
**Target Duration**: 3–5 Minutes (300 seconds max)  
**Live Demo URL**: [http://localhost:5173/demo](http://localhost:5173/demo) (or production Cloud Run URL)  

---

## Presentation Ground Rules
1. **Focus Exclusively on the Running Application**: Never switch to GCP Console, terminal windows, code editors, or API debuggers.
2. **Deterministic Flow**: Use the built-in 1-Click Guided Demo Flow (`/demo`) which deterministically executes the entire shortage lifecycle.
3. **Backup Fallback**: If internet connectivity is interrupted, the application automatically uses stored deterministic demo fallback data clearly labeled as such.

---

## Second-by-Second Presentation Script

### 0:00–0:30 — The Problem (Overview Dashboard)
* **Screen**: Main Dashboard (`/` or `/demo`) showing the National Command Center.
* **Action**: Pan across the high-level KPI cards (Clinics Monitored, Medicine Stocks, Bed Occupancy, Active Alerts).
* **Narration**:
  > *"Judges, healthcare systems don't fail only because resources are unavailable. They can fail because decision-makers don't know where shortages are developing until it is too late.*
  > 
  > *In India's vast network of rural Primary Health Centres, medicine stock-outs are often discovered only when an ill patient arrives at an empty pharmacy shelf. Swasthya Records creates an intelligence layer across the PHC network to predict resource pressure before it becomes a crisis."*

---

### 0:30–1:00 — National Unified Operational View
* **Screen**: Leaflet GIS map with 33 sentinel facilities across Bihar, Uttar Pradesh, and Maharashtra.
* **Action**: Click state filter ("Bihar"), select a district ("Patna"), and click a sentinel facility marker.
* **Narration**:
  > *"The platform provides a unified operational view from the national level down to individual PHCs.*
  > 
  > *Here, every facility is mapped with its sanctioned bed capacity, staffing, and 20 essential NLEM medicines. State and district health officers have instant role-based access to their jurisdiction, while national leaders see the macro supply-chain health of the entire country."*

---

### 1:00–1:40 — Trigger Event: Monsoon Flood Surge
* **Screen**: Guided Demo Flow (`/demo`), Step 2.
* **Action**: Click **"Execute Next Step"** to trigger the Monsoon Flood Surge (+40% demand surge in Patna).
* **Narration**:
  > *"Let's see what happens during a climate shock. A sudden monsoon flood crisis hits Patna District.*
  > 
  > *Outpatient footfall jumps by 40%. Patients arrive with waterborne gastrointestinal illnesses, causing consumption of Oral Rehydration Salts (ORS) and Paracetamol to accelerate dramatically.*
  > 
  > *Instead of waiting for inventory to hit zero, our predictive machine learning layer immediately identifies that consumption is accelerating and recalculates the 14-day forward burn rate."*

---

### 1:40–2:10 — Proactive Early Warning Alert
* **Screen**: Step 4 of `/demo` (or `/alerts`).
* **Action**: Open the Critical Shortage Alert for **Patna Sadar Primary Health Centre (PHC-071 / PHC-001)**. Expand the evidence drawer.
* **Narration**:
  > *"Here is the early warning. The system detects that at the accelerated consumption rate, Patna Sadar will completely exhaust its ORS stock in just 1.4 days.*
  > 
  > *Notice that the platform doesn't just produce an alarming red badge. It shows the concrete mathematical evidence: current inventory of 120 units, projected burn rate of 185 units per day, and lead time of 3 days. The shortage is flagged 48 hours before the clinic runs dry."*

---

### 2:10–2:40 — Grounded Gemini Operations Copilot
* **Screen**: Step 5 of `/demo` (or floating Copilot drawer).
* **Action**: Click the voice microphone or query prompt: *"Why is this clinic at critical risk and can another clinic help?"*
* **Narration**:
  > *"Health administrators need explainable answers, not black-box predictions. The officer asks Gemini Copilot.*
  > 
  > *Gemini acts as an operations copilot. It doesn't invent answers or hallucinate stock numbers—it queries our deterministic forecasting, inventory, and redistribution tools. It clearly explains that the flood surge multiplied consumption, and suggests finding a nearby helper clinic with surplus stock."*

---

### 2:40–3:20 — Smart Resource Redistribution (OR-Tools)
* **Screen**: Step 6 of `/demo` (or `/redistribution`).
* **Action**: Display the optimal transfer recommendation card.
* **Narration**:
  > *"Now the core engine takes over: cross-district rebalancing using Google OR-Tools.*
  > 
  > *The optimization engine identifies that Danapur Clinic, just 18 km away, holds 850 units of ORS. The solver calculates that Danapur can safely transfer 200 units without pushing its own inventory below its 7-day safety threshold.*
  > 
  > *It displays transit distance, estimated travel time of 1.2 hours, and total supply-chain cost."*

---

### 3:20–3:45 — Sandboxed Digital Twin Simulation
* **Screen**: Step 7 of `/demo`.
* **Action**: Click **"Approve & Simulate Transfer"**. Observe before/after comparison.
* **Narration**:
  > *"Before executing any physical truck or dispatch, decision-makers can simulate the intervention.*
  > 
  > *With one click, the transfer is simulated in the sandbox. Look at the result: Patna Sadar's stock runway jumps from 1.4 days to 14.2 days. The risk drops from URGENT to SAFE. The shortage has been prevented before a single patient was turned away."*

---

### 3:45–4:10 — Multi-Tier India Scale
* **Screen**: Hierarchy view / State-District filters.
* **Narration**:
  > *"This is not a single-city prototype. The architecture is built strictly around India's administrative hierarchy: National MoHFW $\rightarrow$ State Health Directorate $\rightarrow$ District CMO $\rightarrow$ Block CHC $\rightarrow$ Village PHC.*
  > 
  > *The same modular system scales seamlessly across 36 States and Union Territories."*

---

### 4:10–4:30 — Google Cloud & AI Technology Stack
* **Screen**: System Status or Architecture Diagram (`docs/architecture.png`).
* **Narration**:
  > *"Under the hood, Swasthya Records leverages Google Cloud technologies built for scale:*
  > 
  > *1. Google Cloud Run for non-root, auto-scaling serverless containers.*  
  > *2. Google BigQuery for federated analytical storage of public MoHFW and HMIS datasets.*  
  > *3. Gemini 2.5 Flash on Vertex AI for natural language reasoning.*  
  > *4. Google OR-Tools for Mixed-Integer Linear Programming optimization.*  
  > *5. Web Speech API for voice-driven accessibility in English and Hindi."*

---

### 4:30–4:50 — Measurable Real-World Impact & Closing
* **Screen**: Overview Dashboard (all metrics green, healthy status).
* **Narration**:
  > *"Our mission is clear: move public healthcare logistics from reactive crisis management to proactive, predictive resilience.*
  > 
  > *Swasthya Records empowers health officers to predict demand surges earlier, prioritize the most vulnerable clinics, find safe surplus supplies nearby, and explain every decision with trusted AI.*
  > 
  > *Thank you. We are ready for your questions."*

---

## Emergency Fallback Protocol (If Offline)
If internet drops during live judging:
1. Click **"Reset to Normal"** on `/demo`.
2. The UI automatically displays the stored deterministic demo simulation with the badge: **"Demo Fallback Data"**.
3. All 7 steps continue to execute smoothly with zero error popups.
