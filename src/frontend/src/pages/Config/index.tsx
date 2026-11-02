import { useEffect, useState } from 'react';
import { Helmet } from 'react-helmet-async';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  FormControl,
  FormControlLabel,
  Grid,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Switch,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material';
import {
  Extension as ExtensionIcon,
  Notifications as NotificationsIcon,
  Save as SaveIcon,
  Security as SecurityIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useSnackbar } from 'notistack';
import { settingsService } from '../../services/settings';
import type { PlatformSettings } from '../../services/settings';
import { getErrorMessage } from '../../services/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`config-tabpanel-${index}`}
      aria-labelledby={`config-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: { xs: 2, sm: 3 } }}>{children}</Box>}
    </div>
  );
}

const configSections = [
  { id: 'general', label: 'General Settings', icon: <SettingsIcon /> },
  { id: 'security', label: 'Security', icon: <SecurityIcon /> },
  { id: 'integrations', label: 'Integrations', icon: <ExtensionIcon /> },
  { id: 'notifications', label: 'Notifications', icon: <NotificationsIcon /> },
];

const Config = () => {
  const { enqueueSnackbar } = useSnackbar();
  const [tabValue, setTabValue] = useState(0);
  const [settings, setSettings] = useState<PlatformSettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const [showSuccess, setShowSuccess] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const response = await settingsService.getSettings();
        if (!cancelled) {
          setSettings(response.settings);
          setError('');
        }
      } catch (err) {
        if (!cancelled) {
          setError(getErrorMessage(err));
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  const updateSection = <K extends keyof PlatformSettings>(
    section: K,
    patch: Partial<PlatformSettings[K]>,
  ) => {
    setSettings((current) =>
      current ? { ...current, [section]: { ...current[section], ...patch } } : current,
    );
  };

  const handleSave = async () => {
    if (!settings) {
      return;
    }
    setIsSaving(true);
    setError('');
    try {
      const response = await settingsService.updateSettings(settings);
      setSettings(response.settings);
      setShowSuccess(true);
      enqueueSnackbar('Configuration saved', { variant: 'success' });
      window.setTimeout(() => setShowSuccess(false), 3000);
    } catch (err) {
      const message = getErrorMessage(err);
      setError(message);
      enqueueSnackbar(message, { variant: 'error' });
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px" role="status">
        <CircularProgress />
      </Box>
    );
  }

  if (!settings) {
    return (
      <Box sx={{ pb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Configuration Management
        </Typography>
        <Alert severity="error">{error || 'Settings are unavailable.'}</Alert>
      </Box>
    );
  }

  return (
    <>
      <Helmet>
        <title>Configuration Management - AI Safety Governance Platform</title>
        <meta
          name="description"
          content="Manage system settings, security configurations, integrations, and notifications"
        />
      </Helmet>

      <Box sx={{ pb: 4 }}>
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          mb={4}
          gap={2}
          flexWrap="wrap"
        >
          <Typography variant="h4" component="h1">
            Configuration Management
          </Typography>
          <Button
            variant="contained"
            startIcon={isSaving ? <CircularProgress size={16} color="inherit" /> : <SaveIcon />}
            onClick={() => void handleSave()}
            disabled={isSaving}
          >
            {isSaving ? 'Saving...' : 'Save Changes'}
          </Button>
        </Box>

        {showSuccess && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Configuration saved successfully.
          </Alert>
        )}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Alert severity="info" sx={{ mb: 2 }}>
          Only non-secret settings are stored here. Webhooks, API tokens and credentials must be
          provided through environment variables or a secrets manager.
        </Alert>

        <Paper sx={{ width: '100%' }}>
          <Tabs
            value={tabValue}
            onChange={(_event, newValue: number) => setTabValue(newValue)}
            aria-label="configuration tabs"
            variant="scrollable"
            allowScrollButtonsMobile
            sx={{ borderBottom: 1, borderColor: 'divider' }}
          >
            {configSections.map((section) => (
              <Tab
                key={section.id}
                icon={section.icon}
                label={section.label}
                iconPosition="start"
                sx={{ minHeight: 64, textTransform: 'none', px: 2 }}
              />
            ))}
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Platform Name"
                  value={settings.general.platform_name}
                  onChange={(e) => updateSection('general', { platform_name: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel id="environment-label">Environment</InputLabel>
                  <Select
                    labelId="environment-label"
                    value={settings.general.environment}
                    label="Environment"
                    onChange={(e) =>
                      updateSection('general', {
                        environment: e.target.value as PlatformSettings['general']['environment'],
                      })
                    }
                  >
                    <MenuItem value="development">Development</MenuItem>
                    <MenuItem value="staging">Staging</MenuItem>
                    <MenuItem value="production">Production</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Data Retention (days)"
                  value={settings.general.data_retention_days}
                  onChange={(e) =>
                    updateSection('general', {
                      data_retention_days: Number.parseInt(e.target.value, 10) || 0,
                    })
                  }
                  inputProps={{ min: 1, max: 3650 }}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Max Concurrent Models"
                  value={settings.general.max_concurrent_models}
                  onChange={(e) =>
                    updateSection('general', {
                      max_concurrent_models: Number.parseInt(e.target.value, 10) || 0,
                    })
                  }
                  inputProps={{ min: 1, max: 100 }}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.general.debug_mode}
                      onChange={(e) =>
                        updateSection('general', { debug_mode: e.target.checked })
                      }
                    />
                  }
                  label="Debug Mode"
                />
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel id="password-policy-label">Password Policy</InputLabel>
                  <Select
                    labelId="password-policy-label"
                    value={settings.security.password_policy}
                    label="Password Policy"
                    onChange={(e) =>
                      updateSection('security', {
                        password_policy: e.target
                          .value as PlatformSettings['security']['password_policy'],
                      })
                    }
                  >
                    <MenuItem value="basic">Basic</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="strong">Strong</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Session Timeout (minutes)"
                  value={settings.security.session_timeout}
                  onChange={(e) =>
                    updateSection('security', {
                      session_timeout: Number.parseInt(e.target.value, 10) || 0,
                    })
                  }
                  inputProps={{ min: 1, max: 1440 }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="IP Whitelist"
                  placeholder="Comma-separated IP addresses"
                  value={settings.security.ip_whitelist}
                  onChange={(e) => updateSection('security', { ip_whitelist: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.security.mfa_enabled}
                      onChange={(e) =>
                        updateSection('security', { mfa_enabled: e.target.checked })
                      }
                    />
                  }
                  label="Enable Multi-Factor Authentication (configuration flag)"
                />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.security.audit_logging}
                      onChange={(e) =>
                        updateSection('security', { audit_logging: e.target.checked })
                      }
                    />
                  }
                  label="Enable Audit Logging"
                />
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel id="aws-region-label">AWS Region</InputLabel>
                  <Select
                    labelId="aws-region-label"
                    value={settings.integrations.aws_region}
                    label="AWS Region"
                    onChange={(e) =>
                      updateSection('integrations', { aws_region: e.target.value })
                    }
                  >
                    <MenuItem value="us-east-1">US East (N. Virginia)</MenuItem>
                    <MenuItem value="us-west-2">US West (Oregon)</MenuItem>
                    <MenuItem value="eu-west-1">EU (Ireland)</MenuItem>
                    <MenuItem value="ap-southeast-1">Asia Pacific (Singapore)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel id="monitoring-service-label">Monitoring Service</InputLabel>
                  <Select
                    labelId="monitoring-service-label"
                    value={settings.integrations.monitoring_service}
                    label="Monitoring Service"
                    onChange={(e) =>
                      updateSection('integrations', {
                        monitoring_service: e.target
                          .value as PlatformSettings['integrations']['monitoring_service'],
                      })
                    }
                  >
                    <MenuItem value="cloudwatch">AWS CloudWatch</MenuItem>
                    <MenuItem value="datadog">Datadog</MenuItem>
                    <MenuItem value="prometheus">Prometheus</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={3}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel id="alert-threshold-label">Alert Threshold</InputLabel>
                  <Select
                    labelId="alert-threshold-label"
                    value={settings.notifications.alert_threshold}
                    label="Alert Threshold"
                    onChange={(e) =>
                      updateSection('notifications', {
                        alert_threshold: e.target
                          .value as PlatformSettings['notifications']['alert_threshold'],
                      })
                    }
                  >
                    <MenuItem value="low">Low</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="high">High</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.notifications.email_notifications}
                      onChange={(e) =>
                        updateSection('notifications', {
                          email_notifications: e.target.checked,
                        })
                      }
                    />
                  }
                  label="Email Notifications"
                />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.notifications.slack_notifications}
                      onChange={(e) =>
                        updateSection('notifications', {
                          slack_notifications: e.target.checked,
                        })
                      }
                    />
                  }
                  label="Slack Notifications (requires SLACK_WEBHOOK_URL in the environment)"
                />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.notifications.daily_digest}
                      onChange={(e) =>
                        updateSection('notifications', { daily_digest: e.target.checked })
                      }
                    />
                  }
                  label="Daily Digest"
                />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.notifications.maintenance_alerts}
                      onChange={(e) =>
                        updateSection('notifications', {
                          maintenance_alerts: e.target.checked,
                        })
                      }
                    />
                  }
                  label="Maintenance Alerts"
                />
              </Grid>
            </Grid>
          </TabPanel>
        </Paper>
      </Box>
    </>
  );
};

export default Config;
