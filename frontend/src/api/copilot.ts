import { fetchJson } from './client';

export interface ChatResponse {
  query: string;
  response: string;
  response_en?: string;
  response_hi?: string;
  language: string;
  tools_called: string[];
  evidence: Record<string, any>;
  sources_used?: string[];
  conversation_id: string;
  is_simulation?: boolean;
}

export interface WhatIfResponse {
  facility_id: string;
  medicine_code: string;
  baseline: {
    stock: number;
    daily_demand: number;
    dosa: number;
    risk: string;
  };
  simulated: {
    stock: number;
    daily_demand: number;
    dosa: number;
    risk: string;
  };
  parameters: {
    demand_surge_pct: number;
    delivery_delay_days: number;
    transfer_units: number;
  };
  impact_summary: string;
  is_simulation: boolean;
}

export const copilotApi = {
  chat: async (
    message: string,
    conversationId?: string,
    language = 'en',
    userRole = 'ADMIN',
    userId = 'operator-01'
  ): Promise<ChatResponse> => {
    return fetchJson<ChatResponse>('/copilot/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        language,
        user_role: userRole,
        user_id: userId
      })
    });
  },

  runWhatIf: async (params: {
    facility_id: string;
    medicine_code: string;
    demand_surge_pct: number;
    delivery_delay_days?: number;
    transfer_units?: number;
    user_role?: string;
  }): Promise<WhatIfResponse> => {
    return fetchJson<WhatIfResponse>('/copilot/what-if', {
      method: 'POST',
      body: JSON.stringify({
        facility_id: params.facility_id,
        medicine_code: params.medicine_code,
        demand_surge_pct: params.demand_surge_pct,
        delivery_delay_days: params.delivery_delay_days || 0,
        transfer_units: params.transfer_units || 0,
        user_role: params.user_role || 'ADMIN'
      })
    });
  },

  sendVoice: async (
    audioBase64: string,
    conversationId?: string,
    language = 'en',
    userRole = 'ADMIN'
  ): Promise<any> => {
    return fetchJson<any>('/copilot/voice', {
      method: 'POST',
      body: JSON.stringify({
        audio_base64: audioBase64,
        conversation_id: conversationId,
        language,
        user_role: userRole
      })
    });
  },

  getAuditLog: async (limit = 50) => {
    return fetchJson<{ total_entries: number; audit_log: any[] }>(`/copilot/audit-log?limit=${limit}`);
  },

  getConversationHistory: async (conversationId: string) => {
    return fetchJson<{ conversation_id: string; turns_count: number; history: any[] }>(`/copilot/history?conversation_id=${conversationId}`);
  }
};
