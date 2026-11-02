import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  LinearProgress,
  CircularProgress,
  Tooltip,
  useTheme,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
} from 'recharts';
import { format } from 'date-fns';
import { MetricData, SystemMetrics } from '../../services/monitoring';

interface ResourceUtilizationCardProps {
  currentMetrics: SystemMetrics;
  historicalData: {
    [key: string]: MetricData[];
  };
  isLoading: boolean;
}

const getUtilizationColor = (value: number) => {
  if (value >= 90) return 'error';
  if (value >= 70) return 'warning';
  return 'success';
};

const ResourceUtilizationCard: React.FC<ResourceUtilizationCardProps> = ({
  currentMetrics,
  historicalData,
  isLoading,
}) => {
  const theme = useTheme();

  const resources = [
    { key: 'cpu', label: 'CPU Usage' },
    { key: 'memory', label: 'MEMORY Usage' },
    { key: 'storage', label: 'STORAGE Usage' },
    { key: 'network', label: 'NETWORK Usage' },
  ];

  const hasHistory = Object.values(historicalData).some(
    (samples) => Array.isArray(samples) && samples.length > 0,
  );

  if (isLoading) {
    return (
      <Paper sx={{ p: 3, minHeight: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <CircularProgress role="status" aria-label="Loading resource utilization" />
      </Paper>
    );
  }

  return (
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
        Resource Utilization
      </Typography>

      <Grid container spacing={3}>
        {/* Current Utilization */}
        <Grid item xs={12} md={6}>
          <Box sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Current Usage
            </Typography>
            {resources.map(({ key, label }) => (
              <Box key={key} sx={{ mb: 2 }}>
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    mb: 1,
                  }}
                >
                  <Typography variant="body2" color="text.secondary">
                    {label}
                  </Typography>
                  <Typography variant="body2">
                    {currentMetrics[key as keyof SystemMetrics]}%
                  </Typography>
                </Box>
                <Tooltip title={`${currentMetrics[key as keyof SystemMetrics]}% utilized`}>
                  <LinearProgress
                    variant="determinate"
                    value={currentMetrics[key as keyof SystemMetrics]}
                    color={getUtilizationColor(
                      currentMetrics[key as keyof SystemMetrics]
                    )}
                    aria-label={`${currentMetrics[key as keyof SystemMetrics]}% utilized`}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Tooltip>
              </Box>
            ))}
          </Box>
        </Grid>

        {/* Historical Usage Chart */}
        <Grid item xs={12} md={6}>
          <Box sx={{ height: 300 }} data-testid="resource-utilization-chart">
            {!hasHistory && (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                No historical samples yet. A new sample is recorded every 30 seconds.
              </Typography>
            )}
            <ResponsiveContainer width="100%" height={hasHistory ? '100%' : 0} aspect={2}>
              <LineChart margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={(timestamp) => format(timestamp, 'HH:mm')}
                  type="number"
                  domain={['dataMin', 'dataMax']}
                />
                <YAxis />
                <RechartsTooltip
                  content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      return (
                        <Paper sx={{ p: 1 }}>
                          <Typography variant="body2" sx={{ mb: 1 }}>
                            {format(label as number, 'HH:mm')}
                          </Typography>
                          {payload.map((entry) => {
                            const value = typeof entry.value === 'number' 
                              ? entry.value.toFixed(2) 
                              : entry.value;
                            return (
                              <Typography
                                key={entry.name}
                                variant="body2"
                                sx={{ color: entry.color }}
                              >
                                {entry.name}: {value}%
                              </Typography>
                            );
                          })}
                        </Paper>
                      );
                    }
                    return null;
                  }}
                />
                {resources.map(({ key, label }, index) => (
                  <Line
                    key={key}
                    data={historicalData[key] || []}
                    type="monotone"
                    dataKey="value"
                    name={label}
                    stroke={theme.palette[
                      ['primary', 'secondary', 'error', 'warning'][index] as
                        | 'primary'
                        | 'secondary'
                        | 'error'
                        | 'warning'
                    ].main}
                    dot={false}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default ResourceUtilizationCard;
