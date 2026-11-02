import api from "./api";

export interface MetricData {
  timestamp: number;
  value: number;
}

export interface SystemMetrics {
  cpu: number;
  memory: number;
  storage: number;
  network: number;
}

export interface ModelMetrics {
  activeModels: number;
  responseTime: number;
  errorRate: number;
  requestsPerMinute: number;
  accuracy: number;
  latency: number;
  throughput: number;
}

export interface ModelPerformance {
  modelId: string;
  modelName: string;
  metrics: {
    accuracy: number;
    latency: number;
    throughput: number;
    errorRate: number;
  };
  status: "healthy" | "degraded" | "error";
  lastUpdated: string;
}

export interface MonitoringAlert {
  id: string;
  type: string;
  severity: "low" | "medium" | "high";
  message: string;
  timestamp: string;
}

class MonitoringService {
  async getSystemMetrics(): Promise<SystemMetrics> {
    const response = await api.get<SystemMetrics>("/monitoring/system");
    return response.data;
  }

  async getModelMetrics(): Promise<ModelMetrics> {
    const response = await api.get<ModelMetrics>("/monitoring/models/metrics");
    return response.data;
  }

  async getPerformanceData(): Promise<MetricData[]> {
    const response = await api.get<MetricData[]>("/monitoring/performance");
    return response.data;
  }

  async getModelPerformance(): Promise<ModelPerformance[]> {
    const response = await api.get<ModelPerformance[]>(
      "/monitoring/models/performance",
    );
    return response.data;
  }

  async getResourceUtilization(resource: string): Promise<MetricData[]> {
    const response = await api.get<MetricData[]>(
      `/monitoring/resources/${resource}`,
    );
    return response.data;
  }

  async getAlerts(): Promise<MonitoringAlert[]> {
    const response = await api.get<MonitoringAlert[]>("/monitoring/alerts");
    return response.data;
  }
}

export const monitoringService = new MonitoringService();
