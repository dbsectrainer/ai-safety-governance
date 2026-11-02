import { useCallback, useEffect, useState } from 'react';
import { Helmet } from 'react-helmet-async';
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Divider,
  Fade,
  Grid,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Tooltip,
  Typography,
  useTheme,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Download as DownloadIcon,
  Error as ErrorIcon,
  Lock as LockIcon,
  Refresh as RefreshIcon,
  Schedule as ScheduleIcon,
  Security as SecurityIcon,
  Settings as SettingsIcon,
  Shield as ShieldIcon,
  VpnKey as VpnKeyIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { useNavigate } from 'react-router-dom';
import { useSnackbar } from 'notistack';
import { securityService } from '../../services/security';
import type { SecuritySummary } from '../../services/security';
import { getErrorMessage } from '../../services/api';

const Security = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const [summary, setSummary] = useState<SecuritySummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState('');

  const loadData = useCallback(async (background = false) => {
    if (background) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }
    try {
      const data = await securityService.getSummary();
      setSummary(data);
      setError('');
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const handleExportReport = () => {
    if (!summary) {
      return;
    }
    const blob = new Blob([JSON.stringify(summary, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `security-report-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    enqueueSnackbar('Security report downloaded', { variant: 'success' });
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px" role="status">
        <CircularProgress />
      </Box>
    );
  }

  if (error || !summary) {
    return (
      <Box sx={{ pb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Security Overview
        </Typography>
        <Alert
          severity="error"
          action={
            <Button color="inherit" size="small" onClick={() => void loadData()}>
              Retry
            </Button>
          }
        >
          {error || 'Security data is unavailable.'}
        </Alert>
      </Box>
    );
  }

  const metrics = [
    {
      id: 'score',
      title: 'Security Score',
      value: `${summary.metrics.security_score}%`,
      icon: <ShieldIcon color="primary" sx={{ fontSize: 40 }} />,
      description: 'Observable security checks currently passing',
      status: summary.metrics.security_score >= 80 ? 'success' : 'warning',
    },
    {
      id: 'users',
      title: 'Active Users',
      value: summary.metrics.active_users,
      icon: <LockIcon color="primary" sx={{ fontSize: 40 }} />,
      description: 'Enabled user accounts',
      status: 'success',
    },
    {
      id: 'policies',
      title: 'Access Policies',
      value: summary.metrics.access_policies,
      icon: <VpnKeyIcon color="primary" sx={{ fontSize: 40 }} />,
      description: 'Roles defined for role-based access control',
      status: summary.metrics.access_policies > 0 ? 'success' : 'warning',
    },
    {
      id: 'events',
      title: 'Events (24h)',
      value: summary.metrics.events_24h,
      icon: <SecurityIcon color="primary" sx={{ fontSize: 40 }} />,
      description: 'Audit events recorded in the last 24 hours',
      status: 'success',
    },
  ] as const;

  return (
    <>
      <Helmet>
        <title>Security Overview - AI Safety Governance Platform</title>
        <meta
          name="description"
          content="Monitor and manage security metrics, events, and recommendations for AI systems"
        />
      </Helmet>

      <Box sx={{ pb: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4} gap={2}>
          <Typography variant="h4" component="h1">
            Security Overview
          </Typography>
          <Box display="flex" alignItems="center" gap={1}>
            <Tooltip title="Refresh data">
              <IconButton
                onClick={() => void loadData(true)}
                disabled={isRefreshing}
                aria-label="Refresh security data"
              >
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Security settings">
              <IconButton aria-label="Security settings" onClick={() => navigate('/config')}>
                <SettingsIcon />
              </IconButton>
            </Tooltip>
            <Button variant="contained" startIcon={<DownloadIcon />} onClick={handleExportReport}>
              Export Report
            </Button>
          </Box>
        </Box>

        <Grid container spacing={3}>
          {metrics.map((metric) => (
            <Grid item xs={12} md={6} lg={3} key={metric.id}>
              <Fade in timeout={400}>
                <Paper sx={{ p: 3, height: '100%' }}>
                  <Box display="flex" alignItems="flex-start" justifyContent="space-between" mb={2}>
                    <Box display="flex" alignItems="center" gap={2}>
                      {metric.icon}
                      <Box>
                        <Typography variant="h6">{metric.title}</Typography>
                        <Typography variant="h4" color="primary" sx={{ mt: 1 }}>
                          {metric.value}
                        </Typography>
                      </Box>
                    </Box>
                    <Chip
                      size="small"
                      icon={
                        metric.status === 'success' ? (
                          <CheckCircleIcon />
                        ) : (
                          <WarningIcon />
                        )
                      }
                      label={metric.status}
                      color={metric.status}
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {metric.description}
                  </Typography>
                </Paper>
              </Fade>
            </Grid>
          ))}

          <Grid item xs={12} md={6}>
            <Fade in timeout={400}>
              <Paper sx={{ p: 3, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  Control Checks
                </Typography>
                <List>
                  {summary.checks.map((check, index) => (
                    <Box key={check.name}>
                      <ListItem>
                        <ListItemIcon>
                          {check.passed ? (
                            <CheckCircleIcon color="success" />
                          ) : (
                            <ErrorIcon color="error" />
                          )}
                        </ListItemIcon>
                        <ListItemText
                          primary={check.name.replace('_', ' ')}
                          secondary={check.description}
                        />
                      </ListItem>
                      {index < summary.checks.length - 1 && <Divider />}
                    </Box>
                  ))}
                </List>
              </Paper>
            </Fade>
          </Grid>

          <Grid item xs={12} md={6}>
            <Fade in timeout={400}>
              <Paper sx={{ p: 3, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  Recent Security Events
                </Typography>
                {summary.events.length === 0 ? (
                  <Typography variant="body2" color="text.secondary">
                    No audit events recorded in the last 24 hours.
                  </Typography>
                ) : (
                  <List>
                    {summary.events.map((event, index) => (
                      <Box key={event.id}>
                        <ListItem>
                          <ListItemIcon>
                            {event.type === 'warning' ? (
                              <WarningIcon color="warning" />
                            ) : (
                              <CheckCircleIcon color="success" />
                            )}
                          </ListItemIcon>
                          <ListItemText
                            primary={event.message}
                            secondary={format(new Date(event.timestamp), 'MMM d, yyyy HH:mm')}
                          />
                        </ListItem>
                        {index < summary.events.length - 1 && <Divider />}
                      </Box>
                    ))}
                  </List>
                )}
              </Paper>
            </Fade>
          </Grid>

          <Grid item xs={12}>
            <Fade in timeout={400}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Recommendations
                </Typography>
                <List>
                  {summary.recommendations.map((recommendation, index) => (
                    <Box key={recommendation.id}>
                      <ListItem>
                        <ListItemIcon>
                          {recommendation.status === 'completed' ? (
                            <CheckCircleIcon color="success" />
                          ) : recommendation.status === 'in_progress' ? (
                            <ScheduleIcon color="primary" />
                          ) : (
                            <WarningIcon color="warning" />
                          )}
                        </ListItemIcon>
                        <ListItemText
                          primary={recommendation.message}
                          secondary={
                            <Chip
                              size="small"
                              label={recommendation.priority.toUpperCase()}
                              color={
                                recommendation.priority === 'high'
                                  ? 'error'
                                  : recommendation.priority === 'medium'
                                    ? 'warning'
                                    : 'default'
                              }
                              sx={{ mt: 0.5 }}
                            />
                          }
                        />
                      </ListItem>
                      {index < summary.recommendations.length - 1 && <Divider />}
                    </Box>
                  ))}
                </List>
                <Typography variant="caption" color="text.secondary">
                  Generated {format(new Date(summary.generated_at), 'MMM d, yyyy HH:mm')} ·{' '}
                  {theme.palette.mode} theme
                </Typography>
              </Paper>
            </Fade>
          </Grid>
        </Grid>
      </Box>
    </>
  );
};

export default Security;
