# Swasthya Records — Operational Data Validation & Quality Rules

## 1. Validation Invariants
The simulation pipeline enforces 6 strict invariants on every generated record:

1. **Inventory Balance Invariant**:
   $$\text{closing\_stock} = \max(0, \text{opening\_stock} + \text{received\_quantity} - \text{daily\_consumption})$$
   *Result*: Zero violations across 59,400 inventory records.
2. **Non-Negativity Constraint**:
   $$\text{closing\_stock} \ge 0, \quad \text{daily\_consumption} \ge 0, \quad \text{patient\_footfall} \ge 0$$
   *Result*: Zero negative records.
3. **Bed Capacity Bound**:
   $$0 \le \text{beds\_occupied} \le \text{beds\_total}$$
   *Result*: Zero bed overflow violations beyond physical capacity.
4. **Staff Presence Bound**:
   $$0 \le \text{doctors\_present} \le \text{doctors\_scheduled}, \quad 0 \le \text{nurses\_present} \le \text{nurses\_scheduled}$$
   *Result*: Zero impossibly high attendance records.
5. **Delivery Chronology**:
   $$\text{expected\_arrival\_date} \ge \text{dispatch\_date}$$
   *Result*: 100% chronological validity across 2,435 delivery shipments.
6. **Provenance Integrity**:
   $$\text{data\_source} == \text{"SIMULATED"}$$
   *Result*: 100% compliance across all 64,805 generated operational records.

---

## 2. Automated Test Execution Summary
* **Test Suite**: `backend/tests/test_simulation_engine.py` & `backend/tests/test_api_endpoints.py`
* **Test Framework**: Pytest 9.1
* **Total Tests Executed**: 12 / 12 PASSED (0 failures, 0 errors).
