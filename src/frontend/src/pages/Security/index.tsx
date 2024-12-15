import { useState, useEffect } from 'react';
import { Helmet } from 'react-helmet-async';
import {
  Box,
  Typography,
  Grid,
  Paper,
  CircularProgress,
  IconButton,
  Tooltip,
  Button,
  Chip,
  useTheme,
  Fade,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Shield as ShieldIcon,
  Lock as LockIcon,
  VpnKey as VpnKeyIcon,
  Security as SecurityIcon,
  Refresh as RefreshIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Schedule as ScheduleIcon,
  Settings as SettingsIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';

interface SecurityMetric {
  id: string;
  title: string;
  value: string;
  icon: JSX.Element;
  description: string;
  status: 'success' | 'warning' | 'error';
  lastUpdated: Date;
}

interface SecurityEvent {
  id: string;
  type: 'info' | 'warning' | 'error';
  message: string;
  timestamp: Date;
}

interface SecurityRecommendation {
  id: string;
  message: string;
  priority: 'high' | 'medium' | 'low';
  status: 'pending' | 'in_progress' | 'completed';
}

const SecurityMetricCard = ({ metric }: { metric: SecurityMetric }) => {
  const theme = useTheme();

  return (
    <Fade in timeout={800}>
      <Paper
        sx={{
          p: 3,
          height: '100%',
          transition: 'transform 0.2s, box-shadow 0.2s',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: theme.shadows[8],
          },
        }}
      >
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
              ) : metric.status === 'warning' ? (
                <WarningIcon />
              ) : (
                <ErrorIcon />
              )
            }
            label={metric.status.charAt(0).toUpperCase() + metric.status.slice(1)}
            color={metric.status}
          />
        </Box>
        <Typography variant="body2" color="text.secondary">
          {metric.description}
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
          Last updated: {format(metric.lastUpdated, 'MMM d, yyyy HH:mm')}
        </Typography>
      </Paper>
    </Fade>
  );
};

const Security = () => {
  const theme = useTheme();
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [metrics, setMetrics] = useState<SecurityMetric[]>([
    {
      id: '1',
      title: 'Security Score',
      value: '95%',
      icon: <ShieldIcon color="primary" sx={{ fontSize: 40 }} />,
      description: 'Overall platform security rating based on multiple factors',
      status: 'success',
      lastUpdated: new Date(),
    },
    {
      id: '2',
      title: 'Active Sessions',
      value: '24',
      icon: <LockIcon color="primary" sx={{ fontSize: 40 }} />,
      description: 'Number of currently authenticated user sessions',
      status: 'success',
      lastUpdated: new Date(),
    },
    {
      id: '3',
      title: 'Access Policies',
      value: '12',
      icon: <VpnKeyIcon color="primary" sx={{ fontSize: 40 }} />,
      description: 'Number of active security policies and access controls',
      status: 'warning',
      lastUpdated: new Date(),
    },
    {
      id: '4',
      title: 'Security Events',
      value: '2',
      icon: <SecurityIcon color="primary" sx={{ fontSize: 40 }} />,
      description: 'Number of security incidents detected in the last 24 hours',
      status: 'warning',
      lastUpdated: new Date(),
    },
  ]);

  const [events, setEvents] = useState<SecurityEvent[]>([
    {
      id: '1',
      type: 'warning',
      message: 'Failed login attempt detected',
      timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000),
    },
    {
      id: '2',
      type: 'info',
      message: 'Security policy updated',
      timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000),
    },
    {
      id: '3',
      type: 'info',
      message: 'Access permissions modified',
      timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000),
    },
    {
      id: '4',
      type: 'info',
      message: 'System security scan completed',
      timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000),
    },
  ]);

  const [recommendations, setRecommendations] = useState<SecurityRecommendation[]>([
    {
      id: '1',
      message: 'Enable two-factor authentication for all admin accounts',
      priority: 'high',
      status: 'pending',
    },
    {
      id: '2',
      message: 'Review and update access policies',
      priority: 'medium',
      status: 'in_progress',
    },
    {
      id: '3',
      message: 'Schedule regular security audits',
      priority: 'medium',
      status: 'completed',
    },
    {
      id: '4',
      message: 'Update security monitoring configurations',
      priority: 'low',
      status: 'pending',
    },
  ]);

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        // In a real implementation, we would fetch actual data from the backend
      } catch (error) {
        console.error('Error loading security data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      // In a real implementation, we would fetch fresh data from the backend
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleExportReport = () => {
    // Implementation for exporting security report
    console.log('Exporting security report...');
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

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
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
          <Typography variant="h4" component="h1">
            Security Overview
          </Typography>
          <Box>
            <Tooltip title="Refresh data">
              <IconButton onClick={handleRefresh} disabled={isRefreshing} sx={{ mr: 1 }}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Security settings">
              <IconButton sx={{ mr: 1 }}>
                <SettingsIcon />
              </IconButton>
            </Tooltip>
            <Button
              variant="contained"
              startIcon={<DownloadIcon />}
              onClick={handleExportReport}
            >
              Export Report
            </Button>
          </Box>
        </Box>

        <Grid container spacing={3}>
          {/* Security Metrics */}
          {metrics.map((metric) => (
            <Grid item xs={12} md={6} lg={3} key={metric.id}>
              <SecurityMetricCard metric={metric} />
            </Grid>
          ))}

          {/* Recent Security Events */}
          <Grid item xs={12} md={6}>
            <Fade in timeout={800}>
              <Paper
                sx={{
                  p: 3,
                  height: '100%',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                  },
                }}
              >
                <Typography variant="h6" gutterBottom>
                  Recent Security Events
                </Typography>
                <List>
                  {events.map((event, index) => (
                    <Box key={event.id}>
                      <ListItem>
                        <ListItemIcon>
                          {event.type === 'warning' ? (
                            <WarningIcon color="warning" />
                          ) : event.type === 'error' ? (
                            <ErrorIcon color="error" />
                          ) : (
                            <CheckCircleIcon color="success" />
                          )}
                        </ListItemIcon>
                        <ListItemText
                          primary={event.message}
                          secondary={format(event.timestamp, 'MMM d, yyyy HH:mm')}
                        />
                      </ListItem>
                      {index < events.length - 1 && <Divider />}
                    </Box>
                  ))}
                </List>
              </Paper>
            </Fade>
          </Grid>

          {/* Security Recommendations */}
          <Grid item xs={12} md={6}>
            <Fade in timeout={800}>
              <Paper
                sx={{
                  p: 3,
                  height: '100%',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                  },
                }}
              >
                <Typography variant="h6" gutterBottom>
                  Security Recommendations
                </Typography>
                <List>
                  {recommendations.map((recommendation, index) => (
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
                      {index < recommendations.length - 1 && <Divider />}
                    </Box>
                  ))}
                </List>
              </Paper>
            </Fade>
          </Grid>
        </Grid>
      </Box>
    </>
  );
};

export default Security;
