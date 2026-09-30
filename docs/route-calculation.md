# Swasthya Records — Route & Distance Matrix Calculation

## 1. Overview

Accurate geographic modeling is essential for evaluating medical resource redistribution. Swasthya Records features a dedicated **GeoRoutingService** ([`backend/app/services/geo_routing.py`](file:///C:/Users/Talha/Swasthya%20records/backend/app/services/geo_routing.py)) that computes pairwise road distances, travel durations, and transit feasible corridors across all 33 pilot primary healthcare centres and community hospitals in Bihar, Uttar Pradesh, and Maharashtra.

---

## 2. Distance Computation Methodology

### 2.1 Great-Circle Haversine Formula
Given coordinates $(\phi_1, \lambda_1)$ and $(\phi_2, \lambda_2)$ in radians:

$$\Delta\phi = \phi_2 - \phi_1, \quad \Delta\lambda = \lambda_2 - \lambda_1$$

$$a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)$$

$$c = 2 \cdot \arctan2\left(\sqrt{a}, \sqrt{1 - a}\right)$$

$$d_{\text{great\_circle}} = R_{\text{earth}} \cdot c \quad (R_{\text{earth}} = 6371.0\text{ km})$$

### 2.2 Road Tortuosity Factor Calibration
Direct line-of-sight distance under-represents actual rural Indian road conditions. We apply a calibrated empirical road tortuosity factor:

$$d_{\text{road}} = d_{\text{great\_circle}} \times 1.25$$

---

## 3. Speed & Transit Duration Modeling

Travel speed is modeled dynamically based on jurisdiction and terrain:
- **Intra-District Transfers**: Average speed $= 35\text{ km/h}$ (rural arterial roads, local traffic).
- **Inter-District / Inter-State Transfers**: Average speed $= 50\text{ km/h}$ (state and national highway corridors).

$$\text{Duration (Hours)} = \frac{d_{\text{road}}}{\text{Speed (km/h)}}$$

---

## 4. Route Matrix Storage & BigQuery Integration

The complete $33 \times 33$ pairwise network ($1,056$ directed non-self routes) is pre-computed, cached in-memory with LRU hashing, and persisted to BigQuery table:
- **BigQuery Table**: `arcadeaiagent.swasthyagrid.redistribution_routes`
- **Fields**: `route_id`, `source_id`, `source_name`, `destination_id`, `destination_name`, `origin_lat`, `origin_lng`, `destination_lat`, `destination_lng`, `distance_km`, `duration_hours`, `route_type`.
