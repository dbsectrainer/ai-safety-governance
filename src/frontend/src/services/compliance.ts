import api from './api';

export interface ComplianceRecord {
  id: number;
  regulation_type: string;
  status: 'compliant' | 'non_compliant' | 'needs_review' | string;
  details: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
  next_review_date: string | null;
}

export interface ComplianceSummary {
  score: number;
  total_regulations: number;
  status_counts: Record<string, number>;
  last_run: string | null;
  latest: ComplianceRecord[];
}

export interface ComplianceRunResult {
  summary: {
    total_rules: number;
    compliant_rules: number;
    non_compliant_rules: number;
    error_rules: number;
    score: number;
  };
  report: string;
  records: ComplianceRecord[];
}

export interface AuditLogEntry {
  id: number;
  user_id: number | null;
  action: string;
  resource_type: string;
  resource_id: string | null;
  details: Record<string, unknown>;
  timestamp: string;
}

class ComplianceService {
  async getSummary(): Promise<ComplianceSummary> {
    const response = await api.get<ComplianceSummary>('/compliance/summary');
    return response.data;
  }

  async getRecords(): Promise<ComplianceRecord[]> {
    const response = await api.get<ComplianceRecord[]>('/compliance/records');
    return response.data;
  }

  async runChecks(): Promise<ComplianceRunResult> {
    const response = await api.post<ComplianceRunResult>('/compliance/checks/run');
    return response.data;
  }

  async getAuditLogs(): Promise<AuditLogEntry[]> {
    const response = await api.get<AuditLogEntry[]>('/compliance/audit-logs');
    return response.data;
  }
}

export const complianceService = new ComplianceService();
