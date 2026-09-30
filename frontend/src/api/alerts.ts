import { fetchJson } from './client';
import { EarlyWarningAlert } from '../types';

export const alertsApi = {
  listAlerts: async (filters?: { minSeverity?: string; alertType?: string; facilityId?: string }): Promise<{ total_active_alerts: number; alerts: EarlyWarningAlert[] }> => {
    const params = new URLSearchParams();
    if (filters?.minSeverity) params.append('min_severity', filters.minSeverity);
    if (filters?.alertType) params.append('alert_type', filters.alertType);
    if (filters?.facilityId) params.append('facility_id', filters.facilityId);
    const query = params.toString() ? `?${params.toString()}` : '';
    return fetchJson<{ total_active_alerts: number; alerts: EarlyWarningAlert[] }>(`/alerts${query}`);
  },

  getCriticalAlerts: async (): Promise<{ total_critical_alerts: number; alerts: EarlyWarningAlert[] }> => {
    return fetchJson<{ total_critical_alerts: number; alerts: EarlyWarningAlert[] }>('/alerts/critical');
  },

  getAlertById: async (alertId: string): Promise<EarlyWarningAlert> => {
    return fetchJson<EarlyWarningAlert>(`/alerts/${alertId}`);
  },

  explainAlertWithGemini: async (alertId: string, language = 'en') => {
    return fetchJson<{
      alert_id: string;
      status: string;
      language: string;
      explanation_en: string;
      explanation_hi: string;
      evidence: Record<string, any>;
      recommended_action: string;
    }>('/ai/explain-alert', {
      method: 'POST',
      body: JSON.stringify({ alert_id: alertId, language })
    });
  }
};
