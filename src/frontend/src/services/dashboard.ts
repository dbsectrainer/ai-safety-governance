import api from './api';

export interface DashboardActivity {
  id: string;
  action: string;
  resource_type: string;
  resource_id: string | null;
  timestamp: string;
}

export interface DashboardPerformancePoint {
  timestamp: number;
  users: number;
  models: number;
}

export interface DashboardSummary {
  metrics: {
    active_users: number;
    active_models: number;
    compliance_score: number;
    system_health: string;
  };
  resources: {
    cpu: number;
    memory: number;
    storage: number;
    network: number;
  };
  compliance: {
    score: number;
    total: number;
    status_counts: Record<string, number>;
  };
  activity: DashboardActivity[];
  performance: DashboardPerformancePoint[];
}

class DashboardService {
  async getSummary(): Promise<DashboardSummary> {
    const response = await api.get<DashboardSummary>('/dashboard/summary');
    return response.data;
  }
}

export const dashboardService = new DashboardService();
