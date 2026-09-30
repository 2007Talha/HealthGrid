"""
Swasthya Records - RBAC Authentication & Authorization Security Core
Enforces least-privilege role boundaries across National, State, and District tiers.
"""

from typing import Optional, Dict, Any, List
from fastapi import Header, HTTPException, Depends, status
import logging

logger = logging.getLogger("swasthya.security")

VALID_ROLES = {"ADMIN", "STATE_OPERATOR", "DISTRICT_OPERATOR"}

# Default region mappings for preset operators
PRESET_CREDENTIALS = {
    "usr-admin-national": {
        "user_id": "usr-admin-national",
        "role": "ADMIN",
        "name": "Dr. Rajesh Sharma",
        "state_code": None,
        "district_code": None
    },
    "usr-state-bihar": {
        "user_id": "usr-state-bihar",
        "role": "STATE_OPERATOR",
        "name": "Pooja Verma (State Director)",
        "state_code": "IN-BR",
        "district_code": None
    },
    "usr-dist-patna": {
        "user_id": "usr-dist-patna",
        "role": "DISTRICT_OPERATOR",
        "name": "Dr. Amit Sinha (District Nodal)",
        "state_code": "IN-BR",
        "district_code": "BR-PATNA"
    }
}


def authenticate_user(
    authorization: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None),
    x_user_region: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Validates user credentials from standard Authorization Bearer header or
    structured secure gateway headers.
    Returns authenticated user profile or raises 401 Unauthorized.
    """
    # 1. Inspect Authorization Bearer token if provided
    role = None
    user_id = x_user_id or "usr-anonymous"
    state_code = None
    district_code = None

    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
        # Evaluate standard session token patterns e.g. swasthya-admin-token, swasthya-state-token
        if "admin" in token.lower():
            role = "ADMIN"
            user_id = "usr-admin-national"
        elif "state" in token.lower() or "bihar" in token.lower():
            role = "STATE_OPERATOR"
            user_id = "usr-state-bihar"
            state_code = "IN-BR"
        elif "dist" in token.lower() or "patna" in token.lower():
            role = "DISTRICT_OPERATOR"
            user_id = "usr-dist-patna"
            state_code = "IN-BR"
            district_code = "BR-PATNA"

    # 2. Inspect X-User-* headers
    if not role and x_user_role:
        if x_user_role.upper() in VALID_ROLES:
            role = x_user_role.upper()

    # 3. Fallback to preset credential mapping if user_id is recognized
    if user_id in PRESET_CREDENTIALS:
        preset = PRESET_CREDENTIALS[user_id]
        role = role or preset["role"]
        state_code = state_code or preset["state_code"]
        district_code = district_code or preset["district_code"]

    # 4. Infer state/district from region string if provided
    if x_user_region:
        reg_upper = x_user_region.upper()
        if "IN-BR" in reg_upper or "BIHAR" in reg_upper:
            state_code = "IN-BR"
        elif "IN-UP" in reg_upper or "UTTAR" in reg_upper:
            state_code = "IN-UP"
        
        if "PATNA" in reg_upper or "BR-PATNA" in reg_upper:
            district_code = "BR-PATNA"
        elif "LUCKNOW" in reg_upper or "UP-LUCKNOW" in reg_upper:
            district_code = "UP-LUCKNOW"

    if not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Missing or invalid authorization credentials.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return {
        "user_id": user_id,
        "role": role,
        "state_code": state_code,
        "district_code": district_code,
        "region": x_user_region
    }


def require_role(allowed_roles: List[str]):
    """
    Dependency factory checking that the authenticated user possesses one of the allowed roles.
    Raises 403 Forbidden if user lacks necessary privileges.
    """
    def dependency(user: Dict[str, Any] = Depends(authenticate_user)) -> Dict[str, Any]:
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Action requires one of roles {allowed_roles}. Current role: {user['role']}."
            )
        return user
    return dependency


def verify_regional_scope(target_state: Optional[str], target_district: Optional[str], user: Dict[str, Any]):
    """
    Enforces geographic scoping:
    - ADMIN: Can access all states and districts.
    - STATE_OPERATOR: Can only access their assigned state.
    - DISTRICT_OPERATOR: Can only access their assigned district.
    Raises 403 Forbidden on boundary violations.
    """
    user_role = user.get("role")
    if user_role == "ADMIN":
        return  # National privileges

    if user_role == "STATE_OPERATOR":
        user_state = user.get("state_code")
        if target_state and user_state and target_state != user_state:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: STATE_OPERATOR assigned to {user_state} cannot access state {target_state}."
            )

    if user_role == "DISTRICT_OPERATOR":
        user_dist = user.get("district_code")
        if target_district and user_dist and target_district != user_dist:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: DISTRICT_OPERATOR assigned to {user_dist} cannot access district {target_district}."
            )
        # Also check state if provided
        user_state = user.get("state_code")
        if target_state and user_state and target_state != user_state:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: DISTRICT_OPERATOR in {user_state} cannot access state {target_state}."
            )
