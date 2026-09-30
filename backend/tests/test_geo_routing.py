"""
Unit Tests for Geographic Routing & Distance Matrix Service
"""

import pytest
from backend.app.services.geo_routing import geo_routing_service, GeoRoutingService

def test_haversine_distance_calculation():
    # Patna (25.60, 85.12) to Gaya (24.79, 85.00) ~90 km great circle
    dist = GeoRoutingService.haversine_distance(25.60, 85.12, 24.79, 85.00)
    assert 85.0 <= dist <= 95.0, f"Expected distance ~90 km, got {dist:.2f} km"

def test_facility_location_retrieval():
    loc = geo_routing_service.get_facility_location("PHC-BR-PAT-001")
    assert loc is not None
    assert loc["facility_name"] == "PHC Bakhtiyarpur"
    assert loc["district_name"] == "Patna"
    assert loc["state_name"] == "Bihar"
    assert loc["latitude"] == 25.46
    assert loc["longitude"] == 85.53

def test_route_calculation_and_caching():
    # PHC Bakhtiyarpur to PHC Danapur (both in Patna district)
    route = geo_routing_service.calculate_route("PHC-BR-PAT-001", "PHC-BR-PAT-002")
    assert route["status"] == "SUCCESS"
    assert route["is_same_district"] is True
    assert route["is_same_state"] is True
    assert 40.0 <= route["distance_km"] <= 85.0
    assert route["duration_minutes"] > 0
    assert "h" in route["duration_formatted"] or "m" in route["duration_formatted"]
    
    # Test caching
    route2 = geo_routing_service.calculate_route("PHC-BR-PAT-001", "PHC-BR-PAT-002")
    assert route == route2

def test_unknown_facility_handling():
    route = geo_routing_service.calculate_route("INVALID-ID-001", "PHC-BR-PAT-001")
    assert route["status"] == "LOCATION_NOT_FOUND"
    assert route["distance_km"] == 9999.0
