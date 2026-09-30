# Swasthya Records — Statistical Anomaly Detection

## 1. Objective
Detects syndromic demand surges, unpredicted fever waves, localized epidemic outbreaks, and abnormal footfall spikes before inventory exhaustion occurs.

---

## 2. Methodology
The engine applies a **Rolling Z-Score & Percentage Deviation Filter** over a 7-day sliding historical baseline:
$$Z_t = \frac{Y_t - \mu_{7d}}{\sigma_{7d}}$$
$$\Delta\% = \frac{Y_t - \mu_{7d}}{\max(1.0, \mu_{7d})} \times 100\%$$

---

## 3. Anomaly Severity Thresholds
* **CRITICAL Surge**: $Z_t \ge 3.5$ OR $\Delta\% \ge +80\%$
* **HIGH Surge**: $Z_t \ge 2.8$ OR $\Delta\% \ge +50\%$
* **WARNING Surge**: $Z_t \ge 2.2$ AND $\Delta\% \ge +25\%$
* **NORMAL**: $|Z_t| < 2.2$

---

## 4. Operational Significance
When an anomaly is flagged, it is bundled directly into the **Early Warning Evidence Payload** and propagated to the **Gemini Operations Explainer** as causal evidence.
