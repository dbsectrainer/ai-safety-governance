import axios from 'axios';

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
  status: 'healthy' | 'degraded' | 'error';
  lastUpdated: string;
}

class MonitoringService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = '/api/monitoring'; // Update with your API base URL
  }

  async getSystemMetrics(): Promise<SystemMetrics> {
    try {
      const response = await axios.get(`${this.baseUrl}/system`);
      return response.data;
    } catch (error) {
      console.error('Error fetching system metrics:', error);
      throw error;
    }
  }

  async getModelMetrics(): Promise<ModelMetrics> {
    try {
      const response = await axios.get(`${this.baseUrl}/models/metrics`);
      return response.data;
    } catch (error) {
      console.error('Error fetching model metrics:', error);
      throw error;
    }
  }

  async getPerformanceData(timeRange: string = '24h'): Promise<MetricData[]> {
    try {
      const response = await axios.get(`${this.baseUrl}/performance`, {
        params: { timeRange }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching performance data:', error);
      throw error;
    }
  }

  async getModelPerformance(): Promise<ModelPerformance[]> {
    try {
      const response = await axios.get(`${this.baseUrl}/models/performance`);
      return response.data;
    } catch (error) {
      console.error('Error fetching model performance:', error);
      throw error;
    }
  }

  async getResourceUtilization(resource: string, timeRange: string = '24h'): Promise<MetricData[]> {
    try {
      const response = await axios.get(`${this.baseUrl}/resources/${resource}`, {
        params: { timeRange }
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching ${resource} utilization:`, error);
      throw error;
    }
  }

  async getAlerts(): Promise<any[]> {
    try {
      const response = await axios.get(`${this.baseUrl}/alerts`);
      return response.data;
    } catch (error) {
      console.error('Error fetching alerts:', error);
      throw error;
    }
  }
}

export const monitoringService = new MonitoringService();
