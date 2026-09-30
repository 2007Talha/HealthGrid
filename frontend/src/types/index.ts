export type UserRole = 'ADMIN' | 'STATE_OPERATOR' | 'DISTRICT_OPERATOR';

export interface UserProfile {
  id: string;
  name: string;
  role: UserRole;
  region?: string;
  avatar?: string;
}

export interface Facility {
  facility_id: string;
  facility_name: string;
  facility_type: string;
  state_code: string;
  state_name: string;
  district_code: string;
  district_name: string;
  sanctioned_beds: number;
  latitude: number;
  longitude: number;
  overall_risk?: 'CRITICAL' | 'HIGH' | 'WARNING' | 'NORMAL';
  medicine_risk_count?: number;
  bed_occupancy_pct?: number;
  doctor_attendance_pct?: number;
}

export interface MedicineSummary {
  medicine_code: string;
  medicine_name: string;
  therapeutic_category: string;
  dosage_form: string;
  strength: string;
  is_emergency_essential: boolean;
  unit_packaging: string;
  total_national_stock: number;
  national_daily_consumption: number;
  national_dosa: number;
  facilities_with_shortage: number;
  facilities_with_surplus: number;
  risk_level: 'CRITICAL' | 'HIGH' | 'WARNING' | 'NORMAL';
}

export interface InventoryRecord {
  phc_id: string;
  facility_name?: string;
  medicine_code: string;
  medicine_name?: string;
  record_date: string;
  opening_stock: number;
  received_stock: number;
  daily_consumption: number;
  closing_stock: number;
  current_stock: number;
  reorder_level: number;
  safety_stock: number;
  days_of_stock_available: number;
  stockout_risk_flag: boolean;
}

export interface BedStatus {
  phc_id: string;
  facility_name?: string;
  record_date: string;
  total_beds: number;
  occupied_beds: number;
  available_beds: number;
  occupancy_rate_pct: number;
  overflow_warning: boolean;
}

export interface StaffingStatus {
  phc_id: string;
  facility_name?: string;
  record_date: string;
  doctors_scheduled: number;
  doctors_present: number;
  nurses_scheduled: number;
  nurses_present: number;
  doctor_shortage: boolean;
  nurse_shortage: boolean;
}

export interface DeliveryRecord {
  delivery_id: string;
  phc_id: string;
  facility_name?: string;
  medicine_code: string;
  medicine_name?: string;
  units: number;
  status: 'DELIVERED' | 'IN_TRANSIT' | 'SCHEDULED';
  expected_arrival_date: string;
  actual_arrival_date?: string;
  supplier_name: string;
}

export interface EarlyWarningAlert {
  alert_id: string;
  alert_type: 'MEDICINE_STOCKOUT_RISK' | 'BED_CAPACITY_RISK' | 'STAFF_SHORTAGE_RISK' | string;
  severity: 'CRITICAL' | 'HIGH' | 'WARNING' | 'INFO';
  facility_id: string;
  facility_name: string;
  district: string;
  state: string;
  resource_type: string;
  resource_id?: string;
  resource_name: string;
  current_value: number;
  threshold_value: number;
  days_until_breach: number;
  model_confidence: number;
  recommended_action: string;
  recommended_next_step?: string;
  timestamp: string;
  evidence?: Record<string, any>;
}

export interface ForecastItem {
  date: string;
  predicted_demand?: number;
  predicted_footfall?: number;
  predicted_occupancy?: number;
  p10_lower?: number;
  p50_median?: number;
  p90_upper?: number;
  actual_value?: number;
  model_version?: string;
}

export interface RedistributionShortage {
  phc_id: string;
  facility_name: string;
  district: string;
  state: string;
  medicine_code: string;
  medicine_name: string;
  current_stock: number;
  daily_consumption: number;
  days_of_stock_available: number;
  safety_stock: number;
  shortage_units: number;
  urgency: 'CRITICAL' | 'HIGH' | 'MODERATE';
}

export interface RedistributionSourceCandidate {
  source_id: string;
  facility_name: string;
  district: string;
  state: string;
  current_stock: number;
  daily_consumption: number;
  safety_stock: number;
  usable_surplus: number;
  distance_km: number;
  travel_time_hours: number;
  feasibility_score: number;
}

export interface RedistributionRecommendation {
  recommendation_id: string;
  destination_id: string;
  destination_name: string;
  medicine_code: string;
  medicine_name: string;
  deficit_units: number;
  total_transfer_allocated: number;
  fulfillment_rate_pct: number;
  single_source_mode: boolean;
  sources: Array<{
    source_id: string;
    source_name: string;
    transfer_units: number;
    distance_km: number;
    travel_time_hours: number;
    safe_surplus_remaining: number;
  }>;
  total_distance_km: number;
  max_eta_hours: number;
  objective_cost: number;
  risk_before: string;
  projected_risk_after: string;
  status: string;
  created_at: string;
  recommendation?: string;
  sourceCoords?: { lat: number; lng: number };
  destCoords?: { lat: number; lng: number };
}

export interface SimulationAudit {
  simulation_id: string;
  recommendation_id: string;
  timestamp: string;
  destination_id: string;
  medicine_code: string;
  total_units_transferred: number;
  risk_before: string;
  risk_after: string;
  dosa_before: number;
  dosa_after: number;
  is_simulation: boolean;
}

export interface EmergencyScenario {
  scenario_id: string;
  event_type: string;
  affected_district_ids: string[];
  demand_multiplier: number;
  severity: string;
  duration_days: number;
  facilities_impacted_count: number;
  status: string;
  created_at: string;
}

export interface CopilotMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  language?: 'en' | 'hi';
  evidence?: Record<string, any>;
  sources_used?: string[];
  isSimulation?: boolean;
  timestamp: string;
}

export interface NationalKPIs {
  facilities_monitored: number;
  critical_alerts: number;
  total_active_alerts: number;
  high_risk_facilities: number;
  medicine_shortages: number;
  bed_pressure_pct: number;
  total_beds: number;
  occupied_beds: number;
  available_beds: number;
  staff_availability_pct: number;
  total_staff_scheduled: number;
  total_staff_present: number;
  active_emergencies: number;
  redistribution_opportunities: number;
}
