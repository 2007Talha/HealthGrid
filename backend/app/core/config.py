"""
Swasthya Records - Application Configuration
"""

import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Swasthya Records"
    API_V1_STR: str = "/api/v1"
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "arcadeaiagent")
    BIGQUERY_DATASET: str = os.getenv("BIGQUERY_DATASET", "swasthyagrid")
    BIGQUERY_LOCATION: str = os.getenv("BIGQUERY_LOCATION", "asia-south1")
    
    # Root Paths
    APP_ROOT: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    WORKSPACE_ROOT: str = os.path.dirname(APP_ROOT)
    DATA_DIR: str = os.path.join(WORKSPACE_ROOT, "data")
    GOV_DATA_DIR: str = os.path.join(DATA_DIR, "processed", "government")
    SIM_DATA_DIR: str = os.path.join(DATA_DIR, "processed", "simulated")
    SQLITE_DB_PATH: str = os.path.join(DATA_DIR, "swasthya_operational.db")
    
    # Simulation Parameters
    DEFAULT_SIMULATION_DAYS: int = 90
    DEFAULT_LEAD_TIME_DAYS: int = 5
    
    # Environment & Security
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "swasthyagrid-dev-secret-key")
    ALLOWED_ORIGINS: list[str] = [
        origin.strip() 
        for origin in os.getenv(
            "ALLOWED_ORIGINS", 
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000"
        ).split(",") if origin.strip()
    ]
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

settings = Settings()
