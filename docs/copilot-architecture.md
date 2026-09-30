# SwasthyaGrid AI — Phase 5: Gemini Operations Copilot Architecture

## Executive Summary
The **SwasthyaGrid Copilot** (`SwasthyaGrid AI Assistant`) is a specialized operational intelligence agent built for public health administrators, state resource directors, and district chief medical officers. It bridges complex predictive time-series models, stock-out risk evaluators, and Mixed Integer Linear Programming (MILP) redistribution engines with an intuitive natural-language and voice interface.

---

## Architectural Principles & Strict Guardrails

```mermaid
flowchart TD
    User["Operator / Health Administrator"] -->|Natural Language / Voice Query| API["FastAPI /api/v1/copilot/chat"]
    API --> Intent["Query Intent Classifier & Role Authorizer"]
    
    subgraph "Deterministic Operational Engine (Source of Truth)"
        Intent -->|Tool Dispatch| Tool1["get_national_summary()"]
        Intent -->|Tool Dispatch| Tool2["get_state_summary(state)"]
        Intent -->|Tool Dispatch| Tool3["get_district_summary(district)"]
        Intent -->|Tool Dispatch| Tool4["get_facility_status(phc_id)"]
        Intent -->|Tool Dispatch| Tool5["get_critical_alerts()"]
        Intent -->|Tool Dispatch| Tool6["get_stockout_risks()"]
        Intent -->|Tool Dispatch| Tool7["get_medicine_status()"]
        Intent -->|Tool Dispatch| Tool8["get_forecast()"]
        Intent -->|Tool Dispatch| Tool9["get_redistribution_options()"]
        Intent -->|Tool Dispatch| Tool10["simulate_redistribution()"]
        Intent -->|Tool Dispatch| Tool11["get_emergency_status()"]
        Intent -->|Tool Dispatch| Tool12["get_resource_pressure()"]
    end
    
    subgraph "Isolated Simulation Twin"
        Intent -->|What-If Parameters| ShadowTwin["What-If Shadow Engine<br/>(Zero Production State Alteration)"]
    end

    Tool1 & Tool2 & Tool3 & Tool4 & Tool5 & Tool6 & Tool7 & Tool8 & Tool9 & Tool10 & Tool11 & Tool12 --> Evidence["Verified Grounded Evidence"]
    ShadowTwin --> Evidence
    
    Evidence --> GeminiSynth["Gemini Grounded Reasoning Layer<br/>(English & Hindi Output)"]
    GeminiSynth --> Audit["Immutable Audit Logger<br/>(copilot_audit_log.json)"]
    GeminiSynth --> Response["Operator Dashboard / Audio TTS Response"]
```

### Core Non-Negotiable Guardrails
1. **Gemini is the Reasoning & NL Layer, NOT the Data Store**: All numerical facts, stock quantities, DOSA days, beds, and transfers originate strictly from deterministic backend microservices.
2. **Zero Hallucination Policy**: If data for a facility or medicine is missing, the Copilot explicitly responds: *"There is insufficient evidence to determine this reliably."*
3. **Simulation vs Reality Demarcation**: What-If scenarios and redistribution simulations are explicitly tagged with `WHAT-IF SIMULATION (Isolated Shadow Test - No State Modified)` to ensure operators never confuse recommendations with executed logistics.
4. **Role-Based Access Control**: Strict access boundaries ensure District Operators cannot view cross-state restricted operational data without elevated privileges.
