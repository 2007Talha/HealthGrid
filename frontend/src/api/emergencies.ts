import { fetchJson } from './client';
import { EmergencyScenario } from '../types';

export const emergenciesApi = {
  listActiveEmergencies: async (): Promise<EmergencyScenario[]> => {
    return fetchJson<EmergencyScenario[]>('/emergencies/active');
  },

  triggerEmergency: async (scenario: {
    event_type: string;
    affected_district_ids: string[];
    demand_multiplier: number;
    severity: string;
    duration_days?: number;
  }): Promise<EmergencyScenario> => {
    return fetchJson<EmergencyScenario>('/emergencies/trigger', {
      method: 'POST',
      body: JSON.stringify(scenario)
    });
  },

  clearEmergency: async (scenarioId?: string) => {
    const query = scenarioId ? `?scenario_id=${scenarioId}` : '';
    return fetchJson<{ status: string; message: string }>(`/emergencies/clear${query}`, {
      method: 'POST'
    });
  }
};
