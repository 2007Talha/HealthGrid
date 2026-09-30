"""
Unit Tests for Feature Engineering & Chronological Split Pipeline
"""

import pytest
import pandas as pd
import numpy as np
from backend.app.services.ml_feature_engineering import feature_pipeline

def test_demand_feature_creation():
    df = feature_pipeline.create_medicine_demand_features()
    assert not df.empty, "Feature dataframe should not be empty"
    
    expected_cols = [
        "lag_consumption_1d", "lag_consumption_2d", "lag_consumption_7d", "lag_consumption_14d",
        "rolling_mean_7d", "rolling_std_7d", "rolling_mean_14d", "day_of_week", "is_weekend",
        "patient_footfall", "is_emergency_active"
    ]
    for col in expected_cols:
        assert col in df.columns, f"Missing expected feature column: {col}"
        assert not df[col].isnull().any(), f"Column {col} contains unexpected NaN values"

def test_chronological_split_no_leakage():
    df = feature_pipeline.create_medicine_demand_features()
    train_df, val_df, test_df = feature_pipeline.chronological_split(df, train_pct=0.70, val_pct=0.15)
    
    assert not train_df.empty
    assert not val_df.empty
    assert not test_df.empty
    
    train_max_date = train_df["record_date"].max()
    val_min_date = val_df["record_date"].min()
    val_max_date = val_df["record_date"].max()
    test_min_date = test_df["record_date"].min()
    
    # Verify strict chronological separation
    assert train_max_date < val_min_date, f"Data leakage detected: train_max ({train_max_date}) >= val_min ({val_min_date})"
    assert val_max_date < test_min_date, f"Data leakage detected: val_max ({val_max_date}) >= test_min ({test_min_date})"
