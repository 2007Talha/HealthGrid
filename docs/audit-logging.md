# SwasthyaGrid Copilot — Audit Logging & Compliance

## Overview
Every operational query, tool invocation, parameters payload, and grounded result summary handled by the SwasthyaGrid Copilot is recorded in an immutable append-only audit trail.

---

## Log Schema & Structure
Audit entries are persisted to `data/processed/copilot_audit_log.json` and queryable via `GET /api/v1/copilot/audit-log`.

```json
{
  "log_id": "9b1d8486-599d-4340-97b7-582ecbf81e59",
  "conversation_id": "e2e-phase5-demo-conv-100",
  "timestamp": "2026-08-23T16:30:00.000Z",
  "user_id": "operator-01",
  "user_role": "ADMIN",
  "tool_called": "run_what_if_simulation",
  "tool_parameters": {
    "facility_id": "PHC-BR-PAT-001",
    "surge": 30.0,
    "transfer": 900
  },
  "result_summary": "Facility PHC-BR-PAT-001 simulated outcome: Stock 1020, DOSA 10.2 days, Risk LOW"
}
```

---

## Compliance Guarantees
1. **Traceability**: Every decision recommendation links directly to the user who requested it, the timestamp, and the exact parameters evaluated.
2. **Immutability**: Audit logs are strictly append-only; historical entries cannot be overwritten or deleted by conversational sessions.
3. **Accountability**: Provides oversight for healthcare disaster responses, preventing unauthorized redistribution simulations or ungrounded data claims.
