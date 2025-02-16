import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Chip,
  Tooltip,
  CircularProgress,
  useTheme,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
} from 'recharts';
import { ModelPerformance } from '../../services/monitoring';

interface ModelPerformanceCardProps {
  data: ModelPerformance[];
  isLoading: boolean;
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'healthy':
      return 'success';
    case 'degraded':
      return 'warning';
    case 'error':
      return 'error';
    default:
      return 'default';
  }
};

const ModelPerformanceCard: React.FC<ModelPerformanceCardProps> = ({ data, isLoading }) => {
  const theme = useTheme();

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress />
      </Box>
    );
  }

  const chartData = data.map(model => ({
    name: model.modelName,
    accuracy: model.metrics.accuracy * 100,
    latency: model.metrics.latency,
    throughput: model.metrics.throughput,
    errorRate: model.metrics.errorRate * 100,
  }));

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
        Model Performance
      </Typography>

      <Box sx={{ mb: 3 }}>
        <Grid container spacing={2}>
          {data.map((model) => (
            <Grid item key={model.modelId}>
              <Tooltip title={`Last updated: ${model.lastUpdated}`}>
                <Chip
                  label={`${model.modelName}: ${model.status}`}
                  color={getStatusColor(model.status)}
                  variant="outlined"
                />
              </Tooltip>
            </Grid>
          ))}
        </Grid>
      </Box>

          <Box sx={{ height: 400 }} data-testid="model-performance-chart">
            <ResponsiveContainer width="100%" height="100%" aspect={2}>
          <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis yAxisId="left" orientation="left" stroke={theme.palette.primary.main} />
            <YAxis yAxisId="right" orientation="right" stroke={theme.palette.secondary.main} />
            <RechartsTooltip
              content={({ active, payload, label }) => {
                if (active && payload && payload.length) {
                  return (
                    <Paper sx={{ p: 1 }}>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        {label}
                      </Typography>
                      {payload.map((entry) => (
                        <Typography
                          key={entry.name}
                          variant="body2"
                          sx={{ color: entry.color }}
                        >
                          {entry.name}: {typeof entry.value === 'number' ? entry.value.toFixed(2) : entry.value}
                          {entry.name === 'accuracy' || entry.name === 'errorRate'
                            ? '%'
                            : entry.name === 'latency'
                            ? 'ms'
                            : '/s'}
                        </Typography>
                      ))}
                    </Paper>
                  );
                }
                return null;
              }}
            />
            <Bar
              yAxisId="left"
              dataKey="accuracy"
              name="Accuracy"
              fill={theme.palette.primary.main}
            />
            <Bar
              yAxisId="right"
              dataKey="latency"
              name="Latency"
              fill={theme.palette.secondary.main}
            />
            <Bar
              yAxisId="right"
              dataKey="throughput"
              name="Throughput"
              fill={theme.palette.success.main}
            />
            <Bar
              yAxisId="left"
              dataKey="errorRate"
              name="Error Rate"
              fill={theme.palette.error.main}
            />
          </BarChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
};

export default ModelPerformanceCard;
