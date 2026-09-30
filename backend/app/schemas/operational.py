"""
Swasthya Records - Operational Data Schemas (Pydantic v2)
"""

from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field

class FacilityMasterSchema(BaseModel):
    facility_id: str
    facility_name: str
    facility_type: str
    state_name: str
    state_code: str
    district_name: str
    district_code: str
    latitude: float
    longitude: float
    sanctioned_beds: int
    catchment_population: int
    sanctioned_doctors: int
    sanctioned_nurses: int
    is_cold_chain_enabled: bool
    accessibility_tier: str
    data_source: str = "OFFICIAL_GOVERNMENT"
    provenance_tier: str = "NHA_FACILITY_REGISTRY"

class MedicineReferenceSchema(BaseModel):
    medicine_code: str
    medicine_name: str
    therapeutic_category: str
    dosage_form: str
    strength: str
    route_of_administration: str
    level_of_healthcare_primary: bool
    level_of_healthcare_secondary: bool
    level_of_healthcare_tertiary: bool
    is_emergency_essential: bool
    unit_packaging: str
    standard_shelf_life_months: int
    data_source: str = "OFFICIAL_GOVERNMENT"
    provenance_tier: str = "NLEM_2022"

class PHCOperationalStatusSchema(BaseModel):
    phc_id: str
    facility_name: str
    state_name: str
    district_name: str
    record_date: date
    timestamp: datetime
    
    # Patient Footfall
    patient_footfall: int = Field(ge=0, description="Total daily patient visits")
    opd_patients: int = Field(ge=0, description="Out-patient visits")
    ipd_patients: int = Field(ge=0, description="In-patient admissions")
    fever_syndromic_cases: int = Field(ge=0, description="Fever/epidemic cases")
    
    # Beds
    beds_total: int = Field(ge=0, description="Functional bed capacity")
    beds_occupied: int = Field(ge=0, description="Occupied beds")
    beds_available: int = Field(ge=0, description="Available beds")
    bed_occupancy_rate_pct: float = Field(ge=0.0, le=100.0, description="Bed occupancy rate %")
    
    # Personnel Attendance
    doctors_scheduled: int = Field(ge=0, description="Rostered doctors")
    doctors_present: int = Field(ge=0, description="Physically present doctors")
    nurses_scheduled: int = Field(ge=0, description="Rostered nurses")
    nurses_present: int = Field(ge=0, description="Physically present nurses")
    doctor_shortage_flag: bool = False
    nurse_shortage_flag: bool = False
    
    # Status
    emergency_status: str = "NORMAL"
    data_source: str = "SIMULATED"

class MedicineInventoryStatusSchema(BaseModel):
    phc_id: str
    medicine_code: str
    medicine_name: str
    therapeutic_category: str
    record_date: date
    opening_stock: int = Field(ge=0)
    received_quantity: int = Field(ge=0)
    daily_consumption: int = Field(ge=0)
    closing_stock: int = Field(ge=0)
    reorder_level: int = Field(ge=0)
    safety_stock: int = Field(ge=0)
    days_of_stock_available: float = Field(ge=0.0)
    stock_out_occurred: bool = False
    data_source: str = "SIMULATED"

class DeliveryEventSchema(BaseModel):
    delivery_id: str
    phc_id: str
    facility_name: str
    medicine_code: str
    medicine_name: str
    quantity: int = Field(gt=0)
    dispatch_date: date
    expected_arrival_date: date
    actual_arrival_date: Optional[date] = None
    status: str = Field(description="SCHEDULED, IN_TRANSIT, DELIVERED, DELAYED, CANCELLED")
    data_source: str = "SIMULATED"
