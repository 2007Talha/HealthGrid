# Swasthya Records — PHC Operational Telemetry Simulator Design

## 1. Core Simulation Architecture
The simulator is designed as a stateful, event-driven mathematical stochastic process modeling public healthcare operations across India's hierarchical tiers.

```
                                    CAUSAL SIMULATION CASCADE
   +-----------------------------------------------------------------------------------------+
   |  Catchment Population + Facility Tier (PHC / CHC / DH)                                  |
   |                             |                                                           |
   |                             v                                                           |
   |  [ Base Daily Footfall ] x [ Day-of-Week ] x [ Seasonal Wave ] x [ Emergency Multiplier]|
   |                             |                                                           |
   |                             v                                                           |
   |                 [ Actual Daily Patient Footfall ]                                       |
   |                     /                       \                                           |
   |                    v                         v                                          |
   |      [ OPD Consultations (88%) ]      [ IPD Admissions (12%) ]                          |
   |                    |                         |                                          |
   |                    v                         v                                          |
   |      [ Medicine Dispensing / Day ]    [ Inpatient Bed Occupancy ]                       |
   |                    |                         |                                          |
   |                    v                         v                                          |
   |      [ Inventory Stock Depletion ]    [ Bed Availability & Overflow Pressure ]           |
   |                    |                                                                    |
   |                    v                                                                    |
   |      [ DOSA Calculation & Stock-out Risk Alert Trigger ]                                |
   +-----------------------------------------------------------------------------------------+
```

---

## 2. Mathematical Formulations & Drivers

### 1. Patient Footfall Generation
$$\text{Footfall}_i(t) = \max\left(15, \text{round}\left( \text{BaseFootfall}_i \times \text{DOW}(t) \times \text{Season}(t) \times \prod_{e \in \mathcal{E}} M_e(i, t) \times (1 + \epsilon_t) \right)\right)$$

Where:
* $\text{BaseFootfall}_i = \text{CatchmentPop}_i \times \gamma_{\text{tier}}$ ($\gamma = 0.0010$ for PHC, $0.0014$ for CHC, $0.0018$ for DH).
* $\text{DOW}(t)$: Monday surge ($1.32$), Tuesday-Thursday normal ($1.05$), Friday-Saturday decline ($0.90$), Sunday minimal ($0.38$).
* $\text{Season}(t) = 1.0 + 0.25 \sin\left(\frac{2\pi (t_{\text{yday}} - 150)}{365}\right)$ (Monsoon fever wave in July–August).
* $M_e(i, t)$: Multiplier for active emergency scenario affecting facility $i$'s district ($1.40\times - 2.50\times$).
* $\epsilon_t \sim \mathcal{N}(0, 0.06^2)$: Stochastic gaussian noise.

---

### 2. Inpatient Bed Dynamics
$$\text{BedsOccupied}_i(t) = \min\left(\text{SanctionedBeds}_i, \max\left(0, \text{round}\left( \text{IPD}_i(t) \times \overline{\text{LOS}} \times \eta_t \right)\right)\right)$$

Where:
* $\overline{\text{LOS}} = 2.4$ days (average length of stay in rural/secondary healthcare).
* $\eta_t \sim \mathcal{U}(0.85, 1.15)$: Turnover variation.
* $\text{BedsAvailable}_i(t) = \text{SanctionedBeds}_i - \text{BedsOccupied}_i(t)$.

---

### 3. Inventory Conservation & Restock Trigger
For each medicine $m$ at facility $i$:

$$\text{ClosingStock}_{i,m}(t) = \max\left(0, \text{OpeningStock}_{i,m}(t) + \text{Received}_{i,m}(t) - \text{Consumption}_{i,m}(t)\right)$$

* When $\text{ClosingStock}_{i,m}(t) \le \text{ReorderLevel}_{i,m}$ and no order is in transit $\implies$ Automatic dispatch of replenishment shipment with lead-time $\tau \in [4, 7]$ days.
* When $\text{ArrivalDate} = t \implies \text{Received}_{i,m}(t) = \text{OrderQuantity}_{i,m}$ and shipment status becomes `"DELIVERED"`.
* If $\text{ClosingStock}_{i,m}(t) = 0 \implies \text{StockOutOccurred} = \text{True}$.
