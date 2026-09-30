# Swasthya Records — Optimization Methodology (Google OR-Tools MILP)

## 1. Problem Formulation

When public health infrastructure experiences local supply chain shocks (e.g. epidemics, monsoon floods, supply pipeline delays), immediate inter-facility mutual aid is required. The objective of the **Swasthya Records Optimization Engine** is to allocate surplus medical supplies across facilities efficiently, minimizing logistics friction while preserving clinical safety at donor sites.

---

## 2. Optimization Variables & Parameters

### 2.1 Sets & Indices
- $D$: Set of destination facilities facing shortages (typically evaluated per shortage event).
- $S$: Set of discovered candidate source facilities within maximum operational radius ($R_{\max} = 300\text{ km}$).
- $m$: Essential medicine code being balanced.

### 2.2 Parameters
- $I_s$: Current inventory at source $s$.
- $\text{SS}_s$: Safety stock threshold at source $s$.
- $\bar{D}_s$: Daily forecast burn rate at source $s$.
- $\text{Surplus}_s = \max(0, I_s - \max(\text{SS}_s, 10 \times \bar{D}_s))$: Usable surplus at source $s$.
- $\text{NetNeed}_d$: Quantity required to elevate destination $d$ to 7 days of safe coverage.
- $d_{sd}$: Calibrated road travel distance (km) from source $s$ to destination $d$.
- $t_{sd}$: Estimated transit duration (hours).
- $K$: Maximum allowable source facilities per recommendation (default $K = 2$).

### 2.3 Decision Variables
- $x_{sd} \in \mathbb{Z}_{\ge 0}$: Integer units of medicine $m$ transferred from source $s$ to destination $d$.
- $y_s \in \{0, 1\}$: Binary indicator whether source facility $s$ is activated ($y_s = 1$) or unused ($y_s = 0$).

---

## 3. Objective Function & Constraints

### 3.1 Cost Function
$$\min Z = \sum_{s \in S} \left( c_{\text{dist}} \cdot d_{sd} \cdot x_{sd} + c_{\text{fixed}} \cdot y_s \right)$$

where:
- $c_{\text{dist}} = 1.0$ (penalty per unit-kilometer).
- $c_{\text{fixed}} = 500.0$ (fixed administrative and dispatch dispatch penalty to favor single-source solutions over fragmented shipments).

### 3.2 Constraints
1. **Donor Surplus Protection Constraint**:
   $$x_{sd} \le \text{Surplus}_s \cdot y_s \quad \forall s \in S$$
   *Guarantees no facility dispatches stock below its 10-day emergency reserve.*

2. **Demand Satisfaction Constraint**:
   $$\sum_{s \in S} x_{sd} = \min\left(\text{NetNeed}_d, \sum_{s \in S} \text{Surplus}_s\right)$$

3. **Multi-Source Dispatch Limit**:
   $$\sum_{s \in S} y_s \le K$$
   *Limits coordination complexity by bounding the number of active donor facilities.*

---

## 4. Google OR-Tools CBC Solver Execution

The backend employs Google OR-Tools `pywraplp.Solver.CreateSolver('CBC')`:
- **Optimality Proof**: Solves to global optimality within $<50\text{ ms}$ for typical district cluster graphs.
- **Fallback Heuristic**: If MILP solver returns `INFEASIBLE` or `NOT_SOLVED`, a greedy distance-sorted surplus allocation is deployed as an automated fallback, ensuring uninterrupted high-availability in disaster response scenarios.
