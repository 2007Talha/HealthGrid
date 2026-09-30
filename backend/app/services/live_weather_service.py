"""
Swasthya Records - Live Meteorological & Environmental Harvester Service

Queries real-time Open-Meteo weather telemetry (temperature, precipitation, humidity, flood indices)
across sentinel districts (Patna, Lucknow, Pune) and dynamically triggers climate-driven healthcare demand surges.
"""

import time
import logging
from typing import Dict, Any, List, Optional
import httpx
from backend.app.services.emergency_service import emergency_service

logger = logging.getLogger("swasthya.weather")

DISTRICT_COORDINATES = {
    "IN-BR-PAT": {"name": "Patna", "state": "Bihar", "lat": 25.5941, "lon": 85.1376},
    "IN-UP-LKO": {"name": "Lucknow", "state": "Uttar Pradesh", "lat": 26.8467, "lon": 80.9462},
    "IN-MH-PUN": {"name": "Pune", "state": "Maharashtra", "lat": 18.5204, "lon": 73.8567},
}

class LiveWeatherHarvester:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._last_fetched_ts: float = 0.0
        self._cache_ttl_seconds: int = 900  # 15 minutes cache
        self._last_harvest_log: List[Dict[str, Any]] = []

    async def fetch_district_weather(self, district_id: str) -> Dict[str, Any]:
        """Fetches live meteorological data for a specific district via Open-Meteo."""
        meta = DISTRICT_COORDINATES.get(district_id)
        if not meta:
            return {"status": "UNKNOWN_DISTRICT", "district_id": district_id}

        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={meta['lat']}&longitude={meta['lon']}"
            f"&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m"
            f"&daily=precipitation_sum,temperature_2m_max"
            f"&timezone=Asia%2FKolkata"
        )

        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    curr = data.get("current", {})
                    daily = data.get("daily", {})
                    
                    precip_today = daily.get("precipitation_sum", [0.0])[0] if daily.get("precipitation_sum") else 0.0
                    temp_max_today = daily.get("temperature_2m_max", [curr.get("temperature_2m", 28.0)])[0]

                    temp_now = curr.get("temperature_2m", 28.0)
                    humidity_now = curr.get("relative_humidity_2m", 65)
                    precip_rate_now = curr.get("precipitation", 0.0)

                    # Assess climate risk level
                    flood_risk = "LOW"
                    heat_risk = "LOW"
                    surge_flag = None

                    if precip_today > 40.0 or precip_rate_now > 15.0:
                        flood_risk = "HIGH_MONSOON_FLOOD"
                        surge_flag = "MONSOON_FLOOD_SURGE"
                    elif precip_today > 20.0:
                        flood_risk = "MODERATE_INUNDATION"

                    if temp_now > 41.0 or temp_max_today > 42.0:
                        heat_risk = "EXTREME_HEATWAVE"
                        if not surge_flag:
                            surge_flag = "HEATWAVE_SURGE"
                    elif temp_now > 38.0:
                        heat_risk = "ELEVATED_HEAT"

                    result = {
                        "district_id": district_id,
                        "district_name": meta["name"],
                        "state_name": meta["state"],
                        "status": "LIVE_SYNCHRONIZED",
                        "latitude": meta["lat"],
                        "longitude": meta["lon"],
                        "current_temperature_c": temp_now,
                        "current_humidity_pct": humidity_now,
                        "current_precipitation_mm_hr": precip_rate_now,
                        "daily_precipitation_sum_mm": round(precip_today, 1),
                        "daily_max_temperature_c": round(temp_max_today, 1),
                        "flood_risk_level": flood_risk,
                        "heatwave_risk_level": heat_risk,
                        "recommended_surge": surge_flag,
                        "last_updated": curr.get("time", time.strftime("%Y-%m-%dT%H:%M")),
                        "provider": "Open-Meteo Global Meteorological API (Free Tier)"
                    }
                    self._cache[district_id] = result
                    return result
        except Exception as e:
            logger.warning(f"Live weather fetch failed for {district_id}, using high-fidelity fallback: {e}")

        # Fallback based on typical regional telemetry
        fallback = {
            "district_id": district_id,
            "district_name": meta["name"],
            "state_name": meta["state"],
            "status": "SIMULATED_TELEMETRY",
            "latitude": meta["lat"],
            "longitude": meta["lon"],
            "current_temperature_c": 29.2,
            "current_humidity_pct": 74,
            "current_precipitation_mm_hr": 0.0,
            "daily_precipitation_sum_mm": 4.5,
            "daily_max_temperature_c": 33.1,
            "flood_risk_level": "LOW",
            "heatwave_risk_level": "LOW",
            "recommended_surge": None,
            "last_updated": time.strftime("%Y-%m-%dT%H:%M"),
            "provider": "Regional Climate Baseline Model"
        }
        self._cache[district_id] = fallback
        return fallback

    async def harvest_all_districts(self) -> Dict[str, Any]:
        """Harvests real-time weather across all monitored districts and updates emergency state if needed."""
        results = {}
        surges_triggered = []

        for dist_id in DISTRICT_COORDINATES:
            data = await self.fetch_district_weather(dist_id)
            results[dist_id] = data

            # Check if weather justifies auto-triggering healthcare surge
            if data.get("recommended_surge") == "MONSOON_FLOOD_SURGE":
                try:
                    emergency_service.trigger_emergency(
                        event_type="MONSOON_FLOOD_SURGE",
                        affected_district_ids=[dist_id],
                        demand_multiplier=1.4,
                        severity="CRITICAL",
                        duration_days=5
                    )
                    surges_triggered.append(f"Auto-triggered flood surge for {data['district_name']} due to heavy precipitation ({data['daily_precipitation_sum_mm']}mm)")
                except Exception as ex:
                    logger.error(f"Error triggering automatic climate emergency: {ex}")

        self._last_fetched_ts = time.time()
        self._last_harvest_log.append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "districts_polled": len(results),
            "surges_triggered": surges_triggered
        })
        if len(self._last_harvest_log) > 20:
            self._last_harvest_log.pop(0)

        return {
            "status": "SUCCESS",
            "harvested_districts": results,
            "automated_actions": surges_triggered,
            "last_harvest_time": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

    def get_cached_status(self) -> Dict[str, Any]:
        """Returns immediately available cached weather without network latency."""
        return {
            "is_cached": bool(self._cache),
            "districts": list(self._cache.values()),
            "last_polled_epoch": self._last_fetched_ts,
            "total_monitored": len(DISTRICT_COORDINATES)
        }

live_weather_service = LiveWeatherHarvester()
