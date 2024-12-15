import { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import {
  Box,
  Typography,
  Paper,
  Tabs,
  Tab,
  TextField,
  Switch,
  FormControlLabel,
  Button,
  Grid,
  Divider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  IconButton,
  Tooltip,
  useTheme,
  Fade,
} from '@mui/material';
import {
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Security as SecurityIcon,
  Extension as ExtensionIcon,
  Notifications as NotificationsIcon,
} from '@mui/icons-material';

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
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

interface ConfigSection {
  id: string;
  label: string;
  icon: JSX.Element;
}

const configSections: ConfigSection[] = [
  { id: 'general', label: 'General Settings', icon: <SettingsIcon /> },
  { id: 'security', label: 'Security', icon: <SecurityIcon /> },
  { id: 'integrations', label: 'Integrations', icon: <ExtensionIcon /> },
  { id: 'notifications', label: 'Notifications', icon: <NotificationsIcon /> },
];

const Config = () => {
  const theme = useTheme();
  const [tabValue, setTabValue] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  // General Settings
  const [generalSettings, setGeneralSettings] = useState({
    platformName: 'AI Safety Governance Platform',
    environment: 'production',
    debugMode: false,
    dataRetentionDays: 30,
    maxConcurrentModels: 10,
  });

  // Security Settings
  const [securitySettings, setSecuritySettings] = useState({
    mfaEnabled: true,
    sessionTimeout: 30,
    passwordPolicy: 'strong',
    ipWhitelist: '',
    auditLogging: true,
  });

  // Integration Settings
  const [integrationSettings, setIntegrationSettings] = useState({
    slackWebhook: '',
    githubToken: '',
    awsRegion: 'us-west-2',
    monitoringService: 'cloudwatch',
  });

  // Notification Settings
  const [notificationSettings, setNotificationSettings] = useState({
    emailNotifications: true,
    slackNotifications: false,
    alertThreshold: 'medium',
    dailyDigest: true,
    maintenanceAlerts: true,
  });

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleSave = async () => {
    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
    } catch (error) {
      console.error('Error saving configuration:', error);
    } finally {
      setIsLoading(false);
    }
  };

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
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
          <Typography variant="h4" component="h1">
            Configuration Management
          </Typography>
          <Box>
            <Button
              variant="contained"
              startIcon={<SaveIcon />}
              onClick={handleSave}
              disabled={isLoading}
              sx={{ ml: 2 }}
            >
              Save Changes
            </Button>
          </Box>
        </Box>

        {showSuccess && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Configuration saved successfully!
          </Alert>
        )}

        <Fade in timeout={800}>
          <Paper sx={{ width: '100%' }}>
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              aria-label="configuration tabs"
              sx={{
                borderBottom: 1,
                borderColor: 'divider',
                '& .MuiTab-root': {
                  minHeight: 64,
                  textTransform: 'none',
                },
              }}
            >
              {configSections.map((section, index) => (
                <Tab
                  key={section.id}
                  icon={section.icon}
                  label={section.label}
                  iconPosition="start"
                  sx={{
                    minHeight: 64,
                    px: 3,
                  }}
                />
              ))}
            </Tabs>

            {/* General Settings */}
            <TabPanel value={tabValue} index={0}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Platform Name"
                    value={generalSettings.platformName}
                    onChange={(e) =>
                      setGeneralSettings({ ...generalSettings, platformName: e.target.value })
                    }
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Environment</InputLabel>
                    <Select
                      value={generalSettings.environment}
                      label="Environment"
                      onChange={(e) =>
                        setGeneralSettings({
                          ...generalSettings,
                          environment: e.target.value as string,
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
                    value={generalSettings.dataRetentionDays}
                    onChange={(e) =>
                      setGeneralSettings({
                        ...generalSettings,
                        dataRetentionDays: parseInt(e.target.value),
                      })
                    }
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Max Concurrent Models"
                    value={generalSettings.maxConcurrentModels}
                    onChange={(e) =>
                      setGeneralSettings({
                        ...generalSettings,
                        maxConcurrentModels: parseInt(e.target.value),
                      })
                    }
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={generalSettings.debugMode}
                        onChange={(e) =>
                          setGeneralSettings({
                            ...generalSettings,
                            debugMode: e.target.checked,
                          })
                        }
                      />
                    }
                    label="Debug Mode"
                  />
                </Grid>
              </Grid>
            </TabPanel>

            {/* Security Settings */}
            <TabPanel value={tabValue} index={1}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Password Policy</InputLabel>
                    <Select
                      value={securitySettings.passwordPolicy}
                      label="Password Policy"
                      onChange={(e) =>
                        setSecuritySettings({
                          ...securitySettings,
                          passwordPolicy: e.target.value as string,
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
                    value={securitySettings.sessionTimeout}
                    onChange={(e) =>
                      setSecuritySettings({
                        ...securitySettings,
                        sessionTimeout: parseInt(e.target.value),
                      })
                    }
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="IP Whitelist"
                    placeholder="Enter comma-separated IP addresses"
                    value={securitySettings.ipWhitelist}
                    onChange={(e) =>
                      setSecuritySettings({
                        ...securitySettings,
                        ipWhitelist: e.target.value,
                      })
                    }
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={securitySettings.mfaEnabled}
                        onChange={(e) =>
                          setSecuritySettings({
                            ...securitySettings,
                            mfaEnabled: e.target.checked,
                          })
                        }
                      />
                    }
                    label="Enable Multi-Factor Authentication"
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={securitySettings.auditLogging}
                        onChange={(e) =>
                          setSecuritySettings({
                            ...securitySettings,
                            auditLogging: e.target.checked,
                          })
                        }
                      />
                    }
                    label="Enable Audit Logging"
                  />
                </Grid>
              </Grid>
            </TabPanel>

            {/* Integration Settings */}
            <TabPanel value={tabValue} index={2}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Slack Webhook URL"
                    value={integrationSettings.slackWebhook}
                    onChange={(e) =>
                      setIntegrationSettings({
                        ...integrationSettings,
                        slackWebhook: e.target.value,
                      })
                    }
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="GitHub Token"
                    type="password"
                    value={integrationSettings.githubToken}
                    onChange={(e) =>
                      setIntegrationSettings({
                        ...integrationSettings,
                        githubToken: e.target.value,
                      })
                    }
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>AWS Region</InputLabel>
                    <Select
                      value={integrationSettings.awsRegion}
                      label="AWS Region"
                      onChange={(e) =>
                        setIntegrationSettings({
                          ...integrationSettings,
                          awsRegion: e.target.value as string,
                        })
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
                    <InputLabel>Monitoring Service</InputLabel>
                    <Select
                      value={integrationSettings.monitoringService}
                      label="Monitoring Service"
                      onChange={(e) =>
                        setIntegrationSettings({
                          ...integrationSettings,
                          monitoringService: e.target.value as string,
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

            {/* Notification Settings */}
            <TabPanel value={tabValue} index={3}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Alert Threshold</InputLabel>
                    <Select
                      value={notificationSettings.alertThreshold}
                      label="Alert Threshold"
                      onChange={(e) =>
                        setNotificationSettings({
                          ...notificationSettings,
                          alertThreshold: e.target.value as string,
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
                        checked={notificationSettings.emailNotifications}
                        onChange={(e) =>
                          setNotificationSettings({
                            ...notificationSettings,
                            emailNotifications: e.target.checked,
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
                        checked={notificationSettings.slackNotifications}
                        onChange={(e) =>
                          setNotificationSettings({
                            ...notificationSettings,
                            slackNotifications: e.target.checked,
                          })
                        }
                      />
                    }
                    label="Slack Notifications"
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={notificationSettings.dailyDigest}
                        onChange={(e) =>
                          setNotificationSettings({
                            ...notificationSettings,
                            dailyDigest: e.target.checked,
                          })
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
                        checked={notificationSettings.maintenanceAlerts}
                        onChange={(e) =>
                          setNotificationSettings({
                            ...notificationSettings,
                            maintenanceAlerts: e.target.checked,
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
        </Fade>
      </Box>
    </>
  );
};

export default Config;
