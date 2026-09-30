import { fetchJson } from './client';
import { Facility } from '../types';

export const facilitiesApi = {
  listFacilities: async (filters?: { state_code?: string; district_code?: string; facility_type?: string }): Promise<Facility[]> => {
    const params = new URLSearchParams();
    if (filters?.state_code) params.append('state_code', filters.state_code);
    if (filters?.district_code) params.append('district_code', filters.district_code);
    if (filters?.facility_type) params.append('facility_type', filters.facility_type);
    const query = params.toString() ? `?${params.toString()}` : '';
    return fetchJson<Facility[]>(`/facilities${query}`);
  },

  getFacilityById: async (facilityId: string): Promise<Facility> => {
    return fetchJson<Facility>(`/facilities/${facilityId}`);
  },

  getHierarchyTree: async (): Promise<Record<string, Record<string, any[]>>> => {
    return fetchJson<Record<string, Record<string, any[]>>>('/facilities/geo/hierarchy');
  }
};
