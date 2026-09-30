import { fetchJson } from './client';

export interface BRICSNode {
  country: string;
  node_id: string;
  facilities_reporting: number;
  status: string;
  epsilon: number;
}

export interface SharedPredictiveModel {
  model_id: string;
  target: string;
  collaborating_nodes: string[];
  parameters_aggregated: number;
  accuracy_gain_vs_isolated: string;
}

export interface FederatedStatus {
  status: string;
  federation_protocol: string;
  global_federated_round: number;
  convergence_metric: string;
  global_loss: number;
  privacy_guarantee: string;
  participating_nodes: BRICSNode[];
  shared_predictive_models: SharedPredictiveModel[];
  last_synchronized_at: string;
}

export const federatedApi = {
  getStatus: () => fetchJson<FederatedStatus>('/federated/status'),
  triggerAggregation: () => fetchJson<any>('/federated/aggregate', { method: 'POST' })
};
