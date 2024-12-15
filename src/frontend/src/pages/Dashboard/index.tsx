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
  People as PeopleIcon,
  Psychology as PsychologyIcon,
  VerifiedUser as VerifiedUserIcon,
  MonitorHeart as MonitorHeartIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Notifications as NotificationsIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';

interface DashboardMetric {
  id: string;
  title: string;
  value: string | number;
  icon: JSX.Element;
  status: 'success' | 'warning' | 'error';
  change?: {
    value: number;
    trend: 'up' | 'down';
  };
}

interface ActivityLog {
  id: string;
  type: 'info' | 'warning' | 'error';
  message: string;
  timestamp: Date;
}

interface PerformanceData {
  timestamp: number;
  users: number;
  models: number;
}

const generatePerformanceData = (hours: number): PerformanceData[] => {
  const now = Date.now();
  return Array.from({ length: hours }, (_, i) => ({
    timestamp: now - (hours - i) * 3600000,
    users: Math.floor(120 + Math.random() * 60),
    models: Math.floor(20 + Math.random() * 10),
  }));
};

const MetricCard = ({ metric }: { metric: DashboardMetric }) => {
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
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={2}>
            {metric.icon}
            <Box>
              <Typography variant="h6" color="text.secondary">
                {metric.title}
              </Typography>
              <Typography variant="h4" sx={{ mt: 1 }}>
                {metric.value}
              </Typography>
            </Box>
          </Box>
          {metric.change && (
            <Chip
              size="small"
              icon={metric.change.trend === 'up' ? <CheckCircleIcon /> : <WarningIcon />}
              label={`${metric.change.trend === 'up' ? '+' : '-'}${Math.abs(metric.change.value)}%`}
              color={metric.change.trend === 'up' ? 'success' : 'warning'}
            />
          )}
        </Box>
      </Paper>
    </Fade>
  );
};

const Dashboard = () => {
  const theme = useTheme();
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [metrics, setMetrics] = useState<DashboardMetric[]>([
    {
      id: '1',
      title: 'Active Users',
      value: 150,
      icon: <PeopleIcon sx={{ fontSize: 40, color: theme.palette.primary.main }} />,
      status: 'success',
      change: { value: 12, trend: 'up' },
    },
    {
      id: '2',
      title: 'Active Models',
      value: 24,
      icon: <PsychologyIcon sx={{ fontSize: 40, color: theme.palette.primary.main }} />,
      status: 'success',
      change: { value: 8, trend: 'up' },
    },
    {
      id: '3',
      title: 'Compliance Score',
      value: '98%',
      icon: <VerifiedUserIcon sx={{ fontSize: 40, color: theme.palette.primary.main }} />,
      status: 'success',
      change: { value: 2, trend: 'up' },
    },
    {
      id: '4',
      title: 'System Health',
      value: 'Excellent',
      icon: <MonitorHeartIcon sx={{ fontSize: 40, color: theme.palette.primary.main }} />,
      status: 'success',
    },
  ]);

  const [activityLogs, setActivityLogs] = useState<ActivityLog[]>([
    {
      id: '1',
      type: 'info',
      message: 'New model deployment successful',
      timestamp: new Date(Date.now() - 30 * 60000),
    },
    {
      id: '2',
      type: 'warning',
      message: 'High resource usage detected',
      timestamp: new Date(Date.now() - 2 * 3600000),
    },
    {
      id: '3',
      type: 'info',
      message: 'System backup completed',
      timestamp: new Date(Date.now() - 4 * 3600000),
    },
    {
      id: '4',
      type: 'error',
      message: 'Failed login attempt detected',
      timestamp: new Date(Date.now() - 6 * 3600000),
    },
  ]);

  const [performanceData, setPerformanceData] = useState<PerformanceData[]>([]);

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        setPerformanceData(generatePerformanceData(24));
      } catch (error) {
        console.error('Error loading dashboard data:', error);
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
      setPerformanceData(generatePerformanceData(24));
    } finally {
      setIsRefreshing(false);
    }
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
        <title>Dashboard - AI Safety Governance Platform</title>
        <meta
          name="description"
          content="Overview of AI system metrics, performance, and activity"
        />
      </Helmet>

      <Box sx={{ pb: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
          <Typography variant="h4" component="h1">
            Dashboard
          </Typography>
          <Box>
            <Tooltip title="Refresh data">
              <IconButton onClick={handleRefresh} disabled={isRefreshing} sx={{ mr: 1 }}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Notifications">
              <IconButton>
                <NotificationsIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        <Grid container spacing={3}>
          {/* Metrics */}
          {metrics.map((metric) => (
            <Grid item xs={12} md={6} lg={3} key={metric.id}>
              <MetricCard metric={metric} />
            </Grid>
          ))}

          {/* Performance Chart */}
          <Grid item xs={12}>
            <Fade in timeout={800}>
              <Paper
                sx={{
                  p: 3,
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                  },
                }}
              >
                <Typography variant="h6" gutterBottom>
                  System Performance
                </Typography>
                <Box sx={{ height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="timestamp"
                        tickFormatter={(timestamp) => format(timestamp, 'HH:mm')}
                      />
                      <YAxis />
                      <RechartsTooltip
                        content={({ active, payload }) => {
                          if (active && payload && payload.length) {
                            return (
                              <Paper sx={{ p: 1 }}>
                                <Typography variant="body2">
                                  Time: {format(payload[0].payload.timestamp, 'HH:mm')}
                                </Typography>
                                {payload.map((entry) => (
                                  <Typography key={entry.name} variant="body2">
                                    {entry.name}: {entry.value}
                                  </Typography>
                                ))}
                              </Paper>
                            );
                          }
                          return null;
                        }}
                      />
                      <Line
                        type="monotone"
                        dataKey="users"
                        stroke={theme.palette.primary.main}
                        name="Active Users"
                      />
                      <Line
                        type="monotone"
                        dataKey="models"
                        stroke={theme.palette.secondary.main}
                        name="Active Models"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              </Paper>
            </Fade>
          </Grid>

          {/* Activity Log */}
          <Grid item xs={12}>
            <Fade in timeout={800}>
              <Paper
                sx={{
                  p: 3,
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                  },
                }}
              >
                <Typography variant="h6" gutterBottom>
                  Recent Activity
                </Typography>
                <List>
                  {activityLogs.map((log, index) => (
                    <Box key={log.id}>
                      <ListItem>
                        <ListItemIcon>
                          {log.type === 'error' ? (
                            <ErrorIcon color="error" />
                          ) : log.type === 'warning' ? (
                            <WarningIcon color="warning" />
                          ) : (
                            <CheckCircleIcon color="success" />
                          )}
                        </ListItemIcon>
                        <ListItemText
                          primary={log.message}
                          secondary={format(log.timestamp, 'MMM d, yyyy HH:mm')}
                        />
                      </ListItem>
                      {index < activityLogs.length - 1 && <Divider />}
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

export default Dashboard;
