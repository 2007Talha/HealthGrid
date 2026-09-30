"""
Swasthya Records - Geographic Routing & Distance Matrix Service
Computes real-world road distance, transit ETA, and map-ready coordinates for multi-facility redistribution routing.
"""

import os
import math
import logging
from functools import lru_cache
import pandas as pd
from backend.app.core.config import settings

logger = logging.getLogger("swasthya.routing")

EARTH_RADIUS_KM = 6371.0
ROAD_TORTUOSITY_FACTOR = 1.28  # Accounts for rural road curvature
SPEED_INTRA_DISTRICT_KMPH = 40.0  # Rural/Peri-urban medical transit speed
SPEED_INTER_DISTRICT_KMPH = 55.0  # Highway medical transport speed


class GeoRoutingService:
    def __init__(self):
        self.facilities_df = None
        self._load_facilities()

    def _load_facilities(self):
        fac_file = os.path.join(settings.GOV_DATA_DIR, "clean_facility_master.csv")
        if os.path.exists(fac_file):
            self.facilities_df = pd.read_csv(fac_file)
        else:
            logger.warning(f"Facility master file not found at {fac_file}")
            self.facilities_df = pd.DataFrame()

    def get_facility_location(self, facility_id):
        """Retrieves latitude, longitude, and administrative metadata for a facility."""
        if self.facilities_df is None or self.facilities_df.empty:
            self._load_facilities()

        row = self.facilities_df[self.facilities_df["facility_id"] == facility_id]
        if row.empty:
            return None
        r = row.iloc[0]
        return {
            "facility_id": r["facility_id"],
            "facility_name": r["facility_name"],
            "facility_type": r["facility_type"],
            "district_name": r["district_name"],
            "district_code": r["district_code"],
            "state_name": r["state_name"],
            "state_code": r["state_code"],
            "latitude": float(r["latitude"]),
            "longitude": float(r["longitude"]),
            "accessibility_tier": r["accessibility_tier"],
            "location_precision": "FACILITY_COORDINATES",
        }

    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        """Calculates great-circle distance between two geographic coordinates in kilometers."""
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2.0) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return EARTH_RADIUS_KM * c

    def calculate_route(self, source_id, destination_id):
        """
        Calculates road distance, travel duration, and map visualization payload between source and destination facilities.
        Uses caching and fallback routing.
        """
        source_loc = self.get_facility_location(source_id)
        dest_loc = self.get_facility_location(destination_id)

        if not source_loc or not dest_loc:
            return {
                "source_id": source_id,
                "destination_id": destination_id,
                "distance_km": 9999.0,
                "duration_minutes": 9999.0,
                "duration_formatted": "N/A",
                "is_same_district": False,
                "is_same_state": False,
                "status": "LOCATION_NOT_FOUND",
                "location_precision": "UNKNOWN",
            }

        return self._cached_route(
            source_id,
            dest_loc["facility_id"],
            source_loc["latitude"],
            source_loc["longitude"],
            dest_loc["latitude"],
            dest_loc["longitude"],
            source_loc["district_code"],
            dest_loc["district_code"],
            source_loc["state_code"],
            dest_loc["state_code"],
        )

    @lru_cache(maxsize=1024)
    def _cached_route(
        self,
        source_id,
        dest_id,
        lat1,
        lon1,
        lat2,
        lon2,
        s_dist,
        d_dist,
        s_state,
        d_state,
    ):
        is_same_district = s_dist == d_dist
        is_same_state = s_state == d_state

        raw_dist = self.haversine_distance(lat1, lon1, lat2, lon2)
        road_dist_km = round(raw_dist * ROAD_TORTUOSITY_FACTOR, 1)
        if road_dist_km < 1.0:
            road_dist_km = 1.0

        # Calibrated speed
        speed = (
            SPEED_INTRA_DISTRICT_KMPH if is_same_district else SPEED_INTER_DISTRICT_KMPH
        )
        duration_hours = road_dist_km / speed
        duration_minutes = round(duration_hours * 60.0, 1)

        hours = int(duration_minutes // 60)
        mins = int(duration_minutes % 60)
        formatted_time = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"

        return {
            "source_id": source_id,
            "destination_id": dest_id,
            "distance_km": road_dist_km,
            "duration_minutes": duration_minutes,
            "duration_hours": round(duration_hours, 2),
            "duration_formatted": formatted_time,
            "is_same_district": is_same_district,
            "is_same_state": is_same_state,
            "source_coordinates": {"lat": lat1, "lng": lon1},
            "destination_coordinates": {"lat": lat2, "lng": lon2},
            "location_precision": "FACILITY_COORDINATES",
            "routing_engine": "CALIBRATED_HAVERSINE_ROAD_MATRIX",
            "status": "SUCCESS",
        }


geo_routing_service = GeoRoutingService()
