"""
Swasthya Records - Facilities API Endpoints
Enforces RBAC scoping across National, State, and District operational boundaries.
"""

import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Header, Depends
import pandas as pd
from backend.app.core.config import settings
from backend.app.core.security import authenticate_user, verify_regional_scope, VALID_ROLES

router = APIRouter()

def get_facility_df() -> pd.DataFrame:
    path = os.path.join(settings.GOV_DATA_DIR, "clean_facility_master.csv")
    if not os.path.exists(path):
        raise HTTPException(status_code=500, detail="Facility master dataset not found.")
    return pd.read_csv(path)

@router.get("", summary="List all official registered health facilities")
@router.get("/", include_in_schema=False)
def list_facilities(
    state_code: Optional[str] = Query(None, description="Filter by state (e.g. IN-BR, IN-UP)"),
    district_code: Optional[str] = Query(None, description="Filter by district code (e.g. BR-PATNA)"),
    facility_type: Optional[str] = Query(None, description="Filter by type (PHC, CHC, District Hospital)"),
    authorization: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None),
    x_user_region: Optional[str] = Header(None)
):
    df = get_facility_df()
    
    # Evaluate RBAC if auth headers are present
    if authorization or x_user_role or x_user_region:
        user = authenticate_user(
            authorization=authorization,
            x_user_role=x_user_role,
            x_user_id=x_user_id,
            x_user_region=x_user_region
        )
        # Check target state/district permission
        verify_regional_scope(state_code, district_code, user)
        
        # Enforce automatic scoping if not explicitly requested
        if user["role"] == "STATE_OPERATOR" and user.get("state_code"):
            state_code = user["state_code"]
        elif user["role"] == "DISTRICT_OPERATOR" and user.get("district_code"):
            district_code = user["district_code"]

    if state_code:
        df = df[df["state_code"] == state_code]
    if district_code:
        df = df[df["district_code"] == district_code]
    if facility_type:
        df = df[df["facility_type"] == facility_type]
    return df.to_dict(orient="records")

@router.get("/{facility_id}", summary="Get facility details by ID")
def get_facility_by_id(
    facility_id: str,
    authorization: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None),
    x_user_region: Optional[str] = Header(None)
):
    df = get_facility_df()
    match = df[df["facility_id"] == facility_id]
    if match.empty:
        raise HTTPException(status_code=404, detail=f"Facility {facility_id} not found.")
    
    facility = match.iloc[0].to_dict()

    # Enforce RBAC boundary if credentials provided
    if authorization or x_user_role or x_user_region:
        user = authenticate_user(
            authorization=authorization,
            x_user_role=x_user_role,
            x_user_id=x_user_id,
            x_user_region=x_user_region
        )
        verify_regional_scope(facility.get("state_code"), facility.get("district_code"), user)

    return facility

@router.get("/geo/hierarchy", summary="Get State -> District -> PHC hierarchical tree")
def get_hierarchy_tree(
    authorization: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None),
    x_user_region: Optional[str] = Header(None)
):
    df = get_facility_df()
    
    if authorization or x_user_role or x_user_region:
        user = authenticate_user(
            authorization=authorization,
            x_user_role=x_user_role,
            x_user_id=x_user_id,
            x_user_region=x_user_region
        )
        if user["role"] == "STATE_OPERATOR" and user.get("state_code"):
            df = df[df["state_code"] == user["state_code"]]
        elif user["role"] == "DISTRICT_OPERATOR" and user.get("district_code"):
            df = df[df["district_code"] == user["district_code"]]

    tree = {}
    for state, state_group in df.groupby("state_name"):
        tree[state] = {}
        for dist, dist_group in state_group.groupby("district_name"):
            tree[state][dist] = dist_group[["facility_id", "facility_name", "facility_type", "sanctioned_beds", "latitude", "longitude"]].to_dict(orient="records")
    return tree
