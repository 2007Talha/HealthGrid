import { fetchJson } from './client';

export const simulationApi = {
  getStatus: async () => {
    return fetchJson<{
      is_running: boolean;
      current_simulated_date: string;
      historical_days_generated: number;
      total_facilities_tracked: number;
      total_medicines_tracked: number;
      total_inventory_records: number;
      active_emergency_scenarios: any[];
      last_updated_at: string;
    }>('/simulation/status');
  },

  stepForward: async () => {
    return fetchJson<{
      status: string;
      advanced_to_date: string;
      facilities_simulated: number;
      inventory_records_simulated: number;
    }>('/simulation/step', {
      method: 'POST'
    });
  },

  resetSimulation: async () => {
    return fetchJson<{ status: string; message: string }>('/simulation/reset', {
      method: 'POST'
    });
  },

  generateHistory: async (days = 90) => {
    return fetchJson<{ status: string; message: string; details: any }>(`/simulation/generate-history?days=${days}`, {
      method: 'POST'
    });
  }
};
