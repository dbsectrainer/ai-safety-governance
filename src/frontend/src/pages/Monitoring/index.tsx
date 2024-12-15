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
} from '@mui/material';
import {
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
} from 'recharts';
import RefreshIcon from '@mui/icons-material/Refresh';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import SettingsIcon from '@mui/icons-material/Settings';
import { format } from 'date-fns';

interface MetricData {
  timestamp: number;
  value: number;
}

interface SystemMetrics {
  cpu: number;
  memory: number;
  storage: number;
  network: number;
}

interface ModelMetrics {
  activeModels: number;
  responseTime: number;
  errorRate: number;
  requestsPerMinute: number;
}

// Sample data - would be replaced with real-time data from backend
const generatePerformanceData = (hours: number): MetricData[] => {
  const now = Date.now();
  return Array.from({ length: hours }, (_, i) => ({
    timestamp: now - (hours - i) * 3600000,
    value: 65 + Math.random() * 30,
  }));
};

const Monitoring = () => {
  const theme = useTheme();
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [performanceData, setPerformanceData] = useState<MetricData[]>([]);
  const [systemMetrics] = useState<SystemMetrics>({
    cpu: 45,
    memory: 62,
    storage: 38,
    network: 75,
  });
  const [modelMetrics] = useState<ModelMetrics>({
    activeModels: 12,
    responseTime: 245,
    errorRate: 0.02,
    requestsPerMinute: 1250,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setPerformanceData(generatePerformanceData(24));
      // In a real implementation, we would fetch actual data from the backend
    } catch (error) {
      console.error('Error loading monitoring data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await loadData();
    } finally {
      setIsRefreshing(false);
    }
  };

  const getStatusIcon = (value: number, threshold: number) =>
    value > threshold ? (
      <ErrorIcon fontSize="small" color="error" />
    ) : (
      <CheckCircleIcon fontSize="small" color="success" />
    );

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
        <title>System Monitoring - AI Safety Governance Platform</title>
        <meta
          name="description"
          content="Real-time monitoring of AI system performance, resource usage, and model metrics"
        />
      </Helmet>

      <Box sx={{ pb: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
          <Typography variant="h4" component="h1">
            System Monitoring
          </Typography>
          <Box>
            <Tooltip title="Refresh data">
              <IconButton onClick={handleRefresh} disabled={isRefreshing} sx={{ mr: 1 }}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Configure monitoring settings">
              <IconButton sx={{ mr: 1 }}>
                <SettingsIcon />
              </IconButton>
            </Tooltip>
            <Chip
              icon={<CheckCircleIcon />}
              label="All Systems Operational"
              color="success"
              variant="outlined"
            />
          </Box>
        </Box>

        <Grid container spacing={3}>
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
                <Box sx={{ height: 400 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={performanceData}>
                      <defs>
                        <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                          <stop
                            offset="5%"
                            stopColor={theme.palette.primary.main}
                            stopOpacity={0.8}
                          />
                          <stop
                            offset="95%"
                            stopColor={theme.palette.primary.main}
                            stopOpacity={0}
                          />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="timestamp"
                        tickFormatter={(timestamp) => format(timestamp, 'HH:mm')}
                      />
                      <YAxis />
                      <RechartsTooltip
                        content={({ active, payload }) => {
                          if (active && payload && payload.length) {
                            const value = payload[0].value as number;
                            return (
                              <Paper sx={{ p: 1 }}>
                                <Typography variant="body2">
                                  Time: {format(payload[0].payload.timestamp, 'HH:mm')}
                                </Typography>
                                <Typography variant="body2">
                                  Value: {value.toFixed(2)}%
                                </Typography>
                              </Paper>
                            );
                          }
                          return null;
                        }}
                      />
                      <Legend />
                      <Area
                        type="monotone"
                        dataKey="value"
                        stroke={theme.palette.primary.main}
                        fillOpacity={1}
                        fill="url(#colorValue)"
                        name="Performance Score"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </Box>
              </Paper>
            </Fade>
          </Grid>

          {/* Resource Usage */}
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
                  Resource Usage
                </Typography>
                <Grid container spacing={2}>
                  {Object.entries(systemMetrics).map(([key, value]) => (
                    <Grid item xs={6} key={key}>
                      <Box
                        sx={{
                          p: 2,
                          borderRadius: 1,
                          bgcolor: theme.palette.grey[50],
                        }}
                      >
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{ mb: 1 }}
                        >
                          {key.charAt(0).toUpperCase() + key.slice(1)}
                        </Typography>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="h6">{value}%</Typography>
                          {getStatusIcon(value, 80)}
                        </Box>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            </Fade>
          </Grid>

          {/* Model Metrics */}
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
                  Model Status
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Box
                      sx={{
                        p: 2,
                        borderRadius: 1,
                        bgcolor: theme.palette.grey[50],
                      }}
                    >
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        Active Models
                      </Typography>
                      <Typography variant="h6">{modelMetrics.activeModels}</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box
                      sx={{
                        p: 2,
                        borderRadius: 1,
                        bgcolor: theme.palette.grey[50],
                      }}
                    >
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        Response Time
                      </Typography>
                      <Typography variant="h6">{modelMetrics.responseTime}ms</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box
                      sx={{
                        p: 2,
                        borderRadius: 1,
                        bgcolor: theme.palette.grey[50],
                      }}
                    >
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        Error Rate
                      </Typography>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="h6">{modelMetrics.errorRate}%</Typography>
                        {getStatusIcon(modelMetrics.errorRate, 1)}
                      </Box>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box
                      sx={{
                        p: 2,
                        borderRadius: 1,
                        bgcolor: theme.palette.grey[50],
                      }}
                    >
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        Requests/min
                      </Typography>
                      <Typography variant="h6">
                        {modelMetrics.requestsPerMinute.toLocaleString()}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </Paper>
            </Fade>
          </Grid>
        </Grid>
      </Box>
    </>
  );
};

export default Monitoring;
