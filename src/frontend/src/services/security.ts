import api from "./api";

export interface SecurityCheck {
  name: string;
  passed: boolean;
  description: string;
  severity: "low" | "medium" | "high";
}

export interface SecurityEvent {
  id: string;
  type: "info" | "warning";
  message: string;
  timestamp: string;
}

export interface SecurityRecommendation {
  id: string;
  message: string;
  priority: "low" | "medium" | "high";
  status: "pending" | "in_progress" | "completed";
}

export interface SecuritySummary {
  score: number;
  checks: SecurityCheck[];
  metrics: {
    security_score: number;
    active_users: number;
    access_policies: number;
    events_24h: number;
  };
  events: SecurityEvent[];
  recommendations: SecurityRecommendation[];
  generated_at: string;
}

class SecurityService {
  async getSummary(): Promise<SecuritySummary> {
    const response = await api.get<SecuritySummary>("/security/summary");
    return response.data;
  }
}

export const securityService = new SecurityService();
