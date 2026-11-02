import api from "./api";

export interface GeneralSettings {
  platform_name: string;
  environment: "development" | "staging" | "production";
  debug_mode: boolean;
  data_retention_days: number;
  max_concurrent_models: number;
}

export interface PlatformSecuritySettings {
  mfa_enabled: boolean;
  session_timeout: number;
  password_policy: "basic" | "medium" | "strong";
  ip_whitelist: string;
  audit_logging: boolean;
}

export interface NotificationSettings {
  email_notifications: boolean;
  slack_notifications: boolean;
  alert_threshold: "low" | "medium" | "high";
  daily_digest: boolean;
  maintenance_alerts: boolean;
}

export interface IntegrationSettings {
  aws_region: string;
  monitoring_service: "cloudwatch" | "datadog" | "prometheus";
}

export interface PlatformSettings {
  general: GeneralSettings;
  security: PlatformSecuritySettings;
  notifications: NotificationSettings;
  integrations: IntegrationSettings;
}

export interface SettingsResponse {
  settings: PlatformSettings;
  updated_at: string;
}

class SettingsService {
  async getSettings(): Promise<SettingsResponse> {
    const response = await api.get<SettingsResponse>("/settings");
    return response.data;
  }

  async updateSettings(
    settings: Partial<PlatformSettings>,
  ): Promise<SettingsResponse> {
    const response = await api.put<SettingsResponse>("/settings", settings);
    return response.data;
  }
}

export const settingsService = new SettingsService();
