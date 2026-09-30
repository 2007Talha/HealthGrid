import { fetchJson } from './client';
import { RedistributionShortage, RedistributionSourceCandidate, RedistributionRecommendation, SimulationAudit } from '../types';

export const redistributionApi = {
  getShortages: async (): Promise<{ status: string; total_shortages: number; shortages: RedistributionShortage[] }> => {
    return fetchJson<{ status: string; total_shortages: number; shortages: RedistributionShortage[] }>('/redistribution/shortages');
  },

  getCandidateSources: async (destinationId: string, medicineCode: string, maxDistanceKm = 300.0) => {
    return fetchJson<{ status: string; destination_id: string; medicine_code: string; candidate_count: number; candidates: RedistributionSourceCandidate[] }>(
      `/redistribution/sources?destination_id=${destinationId}&medicine_code=${medicineCode}&max_distance_km=${maxDistanceKm}`
    );
  },

  generateRecommendation: async (destinationId: string, medicineCode: string, maxSources = 2): Promise<RedistributionRecommendation> => {
    return fetchJson<RedistributionRecommendation>('/redistribution/recommend', {
      method: 'POST',
      body: JSON.stringify({
        destination_id: destinationId,
        facility_id: destinationId,
        medicine_code: medicineCode,
        max_sources: maxSources
      })
    });
  },

  simulateTransfer: async (recommendationId: string, recommendationData?: any): Promise<SimulationAudit> => {
    return fetchJson<SimulationAudit>('/redistribution/simulate', {
      method: 'POST',
      body: JSON.stringify({ recommendation_id: recommendationId, recommendation_data: recommendationData })
    });
  },

  resetSimulations: async () => {
    return fetchJson<{ status: string; message: string }>('/redistribution/reset', {
      method: 'POST'
    });
  },

  getSimulationHistory: async (): Promise<{ status: string; total_simulations: number; history: SimulationAudit[] }> => {
    return fetchJson<{ status: string; total_simulations: number; history: SimulationAudit[] }>('/redistribution/history');
  },

  explainRedistribution: async (recommendationId: string, payload?: any, language = 'en') => {
    return fetchJson<{
      status: string;
      language: string;
      explanation_en: string;
      explanation_hi: string;
      evidence: Record<string, any>;
    }>('/ai/explain-redistribution', {
      method: 'POST',
      body: JSON.stringify({ recommendation_id: recommendationId, recommendation_payload: payload, language })
    });
  }
};
