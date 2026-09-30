import { fetchJson } from './client';
import { ForecastItem } from '../types';

export const forecastsApi = {
  getMedicineForecast: async (phcId: string, medicineCode: string, horizonDays = 14) => {
    return fetchJson<{
      phc_id: string;
      medicine_code: string;
      horizon_days: number;
      model_version: string;
      forecasts: ForecastItem[];
    }>(`/forecast/medicine/${phcId}/${medicineCode}?horizon_days=${horizonDays}`);
  },

  getPatientFootfallForecast: async (phcId: string, horizonDays = 7) => {
    return fetchJson<{
      phc_id: string;
      horizon_days: number;
      forecasts: ForecastItem[];
    }>(`/forecast/patients/${phcId}?horizon_days=${horizonDays}`);
  },

  getBedOccupancyForecast: async (phcId: string, horizonDays = 7) => {
    return fetchJson<{
      phc_id: string;
      horizon_days: number;
      forecasts: ForecastItem[];
    }>(`/forecast/beds/${phcId}?horizon_days=${horizonDays}`);
  },

  getEvaluationMetrics: async () => {
    return fetchJson<any>('/forecast/evaluation-metrics');
  }
};
