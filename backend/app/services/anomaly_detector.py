"""
Swasthya Records - Statistical Anomaly Detection Service
Detects abnormal demand surges, unusual footfall spikes, and sudden consumption deviations using rolling Z-Score & IQR bounds.
"""

import numpy as np


class AnomalyDetector:
    def __init__(self, z_threshold=2.2):
        self.z_threshold = z_threshold

    def detect_consumption_anomalies(self, recent_history, current_val):
        """Evaluates whether current consumption deviates abnormally from the 7-day rolling window."""
        if len(recent_history) < 3:
            return {
                "is_anomaly": False,
                "z_score": 0.0,
                "percentage_deviation": 0.0,
                "reason": "Insufficient history",
                "severity": "NORMAL",
            }

        arr = np.array(recent_history[-7:])
        mean = float(np.mean(arr))
        std = float(np.std(arr))

        if std == 0:
            std = max(1.0, mean * 0.1)

        z_score = float((current_val - mean) / std)
        pct_deviation = float((current_val - mean) / max(1.0, mean) * 100.0)

        is_anomaly = abs(z_score) >= self.z_threshold and pct_deviation > 25.0
        severity = "NORMAL"
        if is_anomaly:
            if z_score >= 3.5 or pct_deviation >= 80.0:
                severity = "CRITICAL"
            elif z_score >= 2.8 or pct_deviation >= 50.0:
                severity = "HIGH"
            else:
                severity = "WARNING"

        return {
            "is_anomaly": is_anomaly,
            "z_score": round(z_score, 2),
            "rolling_7d_mean": round(mean, 1),
            "current_value": round(current_val, 1),
            "percentage_deviation": round(pct_deviation, 1),
            "severity": severity,
        }


anomaly_detector = AnomalyDetector()
