# Swasthya Records — Model Evaluation & Baseline Comparison

## 1. Evaluation Methodology
* **Splitting Protocol**: Strict Chronological Splitting (No random cross-validation, zero future data leakage).
  * **Train Period**: First 70% of historical timeline (Days 15–67).
  * **Validation Period**: Middle 15% (Days 68–78).
  * **Test Period**: Most recent 15% (Days 79–90).
* **Baseline Model**: 7-Day Rolling Moving Average:
  $$\hat{Y}_{t}^{\text{Baseline}} = \frac{1}{7}\sum_{k=1}^7 Y_{t-k}$$

---

## 2. Empirical Performance Metrics on Test Set

| Target Variable | Metric | 7-Day MA Baseline | Swasthya ML Model | Performance Improvement |
| :--- | :--- | :--- | :--- | :--- |
| **Medicine Demand** | **MAE** | 18.68 units/day | **12.78 units/day** | **+31.57% Improvement** |
| | **RMSE** | 57.90 | **35.01** | **+39.53% Improvement** |
| | **WAPE** | 17.60% | **12.05%** | **+31.53% Accuracy Gain** |
| **Patient Footfall** | **MAE** | 92.05 visits/day | **49.94 visits/day** | **+45.75% Improvement** |
| | **RMSE** | 224.95 | **93.81** | **+58.30% Improvement** |
| **Bed Occupancy** | **MAE** | 1.95 beds | **1.61 beds** | **+17.23% Improvement** |

---

## 3. Analysis & Key Insights
1. **Day-of-Week Seasonality**: The baseline moving average lags behind Monday surges by 1–2 days. The ML model instantly captures Monday OPD spikes (+32%) and Sunday reductions via calibrated calendar features.
2. **Outbreak Multiplier Propagation**: When an emergency outbreak is declared, the ML model scales demand immediately based on the active indicator, whereas a moving average takes 5–7 days to catch up.
