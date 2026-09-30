# Swasthya Records — Stock-Out Risk & Inventory Coverage Methodology

## 1. Days of Stock Available (DOSA) Formulation
Traditional inventory management divides stock by historical average. Swasthya Records utilizes the **forecasted forward burn rate**:
$$\text{DOSA} = \frac{I_0}{\frac{1}{7}\sum_{k=1}^7 \hat{D}(t+k)}$$
Where $I_0$ is current physical stock and $\hat{D}(t+k)$ is the ML forecasted consumption on day $t+k$.

---

## 2. Dynamic Projected Stock-Out Date
The inventory trajectory is simulated day-by-day over the 14-day forecast horizon by factoring in in-transit delivery arrivals $R(t+k)$:
$$I(t+k) = I(t+k-1) + R(t+k) - \hat{D}(t+k)$$
$$\text{Stock-Out Date} = \min \left\{ t+k \mid I(t+k) \le 0 \right\}$$

If $I(t+k) > 0$ for all $k \in [1, 14]$, the horizon is classified as **Adequate Coverage (>14 days)**.

---

## 3. Safety Stock Formulation
Safety stock buffers against both demand volatility and supplier lead-time variance:
$$\text{Safety Stock} = Z_{\alpha} \cdot \sigma_{\text{demand}} \cdot \sqrt{L} + 3.0 \cdot \overline{D}$$
* $Z_{\alpha} = 1.65$ (95% service level factor)
* $\sigma_{\text{demand}}$: Standard deviation of forecasted demand
* $L = 5$ days (typical district warehouse lead-time)
* $3.0 \cdot \overline{D}$: Minimum 3-day buffer reserve

---

## 4. Multi-Tier Risk Classification Matrix

| Risk Level | Threshold Criteria | Recommended Operational Action |
| :--- | :--- | :--- |
| **CRITICAL** | Stock-out in $< 48$ hours ($\text{DOSA} < 2.0\text{d}$) OR $I_0 = 0$ | Emergency intra-district redistribution dispatch from nearest surplus PHC |
| **HIGH** | Stock-out in $2.0 \le \text{DOSA} < 5.0\text{d}$ | Expedite pending shipment or trigger priority warehouse reorder |
| **WARNING** | $5.0 \le \text{DOSA} < 10.0\text{d}$ OR $I_0 < \text{Safety Stock}$ | Verify scheduled replenishment queue |
| **OPTIMAL / LOW** | $\text{DOSA} \ge 10.0\text{d}$ AND $I_0 \ge \text{Safety Stock}$ | Regular monitoring |
