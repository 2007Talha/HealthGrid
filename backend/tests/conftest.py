"""
Swasthya Records - Pytest Configuration & Fixtures
"""

import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.services.simulation_engine import simulation_engine

@pytest.fixture(scope="session")
def test_client():
    return TestClient(app)

@pytest.fixture(scope="session")
def engine():
    simulation_engine.generate_historical_timeseries(days=14)
    return simulation_engine
