import { fetchJson } from './client';
import { NationalKPIs, MedicineSummary, InventoryRecord, BedStatus, StaffingStatus, DeliveryRecord } from '../types';

export const operationalApi = {
  getNationalKPIs: async (): Promise<NationalKPIs> => {
    return fetchJson<NationalKPIs>('/operational/national-kpi');
  },

  getMedicinesSummary: async (): Promise<{ total_medicines: number; as_of_date: string; medicines: MedicineSummary[] }> => {
    return fetchJson<{ total_medicines: number; as_of_date: string; medicines: MedicineSummary[] }>('/operational/medicines-summary');
  },

  getPHCInventory: async (phcId: string): Promise<{ phc_id: string; total_medicines_tracked: number; inventory: InventoryRecord[] }> => {
    return fetchJson<{ phc_id: string; total_medicines_tracked: number; inventory: InventoryRecord[] }>(`/operational/inventory/${phcId}`);
  },

  getMedicineHistory: async (phcId: string, medicineCode: string): Promise<{ phc_id: string; medicine_code: string; time_series_points: number; history: InventoryRecord[] }> => {
    return fetchJson<{ phc_id: string; medicine_code: string; time_series_points: number; history: InventoryRecord[] }>(`/operational/inventory/history/${phcId}/${medicineCode}`);
  },

  getBedStatus: async (phcId?: string): Promise<{ total_facilities: number; bed_status: BedStatus[] }> => {
    const query = phcId ? `?phc_id=${phcId}` : '';
    return fetchJson<{ total_facilities: number; bed_status: BedStatus[] }>(`/operational/beds${query}`);
  },

  getBedHistory: async (phcId?: string, days = 14): Promise<{ total_days: number; bed_history: BedStatus[] }> => {
    const query = phcId ? `?phc_id=${phcId}&days=${days}` : `?days=${days}`;
    return fetchJson<{ total_days: number; bed_history: BedStatus[] }>(`/operational/beds/history${query}`);
  },

  getStaffingStatus: async (phcId?: string): Promise<{ total_facilities: number; staffing_status: StaffingStatus[] }> => {
    const query = phcId ? `?phc_id=${phcId}` : '';
    return fetchJson<{ total_facilities: number; staffing_status: StaffingStatus[] }>(`/operational/staffing${query}`);
  },

  getDeliveries: async (phcId?: string, inTransitOnly = false): Promise<{ total_deliveries: number; deliveries: DeliveryRecord[] }> => {
    const params = new URLSearchParams();
    if (phcId) params.append('phc_id', phcId);
    params.append('in_transit_only', inTransitOnly.toString());
    return fetchJson<{ total_deliveries: number; deliveries: DeliveryRecord[] }>(`/operational/deliveries?${params.toString()}`);
  },

  getCriticalShortages: async (dosaThreshold = 3.0, bedThresholdPct = 90.0) => {
    return fetchJson<{ stockout_alerts_count: number; stockout_alerts: any[]; bed_overflow_alerts_count: number; bed_overflow_alerts: any[] }>(
      `/operational/critical-alerts?dosa_threshold=${dosaThreshold}&bed_threshold_pct=${bedThresholdPct}`
    );
  }
};
