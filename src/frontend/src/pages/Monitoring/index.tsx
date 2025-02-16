import { useState, useEffect, useCallback } from 'react';
import { Helmet } from 'react-helmet-async';
import {
  Box,
  Typography,
  Grid,
  IconButton,
  Tooltip,
  Chip,
  useTheme,
  Fade,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import SettingsIcon from '@mui/icons-material/Settings';
import { monitoringService } from '../../services/monitoring';
import type { MetricData, SystemMetrics, ModelMetrics, ModelPerformance } from '../../services/monitoring';
import ModelPerformanceCard from '../../components/Monitoring/ModelPerformanceCard';
import ResourceUtilizationCard from '../../components/Monitoring/ResourceUtilizationCard';

interface ResourceHistoricalData {
  [key: string]: MetricData[];
}

const Monitoring = () => {
  const theme = useTheme();
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics>({
    cpu: 0,
    memory: 0,
    storage: 0,
    network: 0,
  });
  const [modelMetrics, setModelMetrics] = useState<ModelMetrics>({
    activeModels: 0,
    responseTime: 0,
    errorRate: 0,
    requestsPerMinute: 0,
    accuracy: 0,
    latency: 0,
    throughput: 0,
  });
  const [modelPerformance, setModelPerformance] = useState<ModelPerformance[]>([]);
  const [resourceHistory, setResourceHistory] = useState<ResourceHistoricalData>({});

  const loadData = useCallback(async () => {
    try {
      const [
        systemMetricsData,
        modelMetricsData,
        modelPerformanceData,
        cpuHistory,
        memoryHistory,
        storageHistory,
        networkHistory,
      ] = await Promise.all([
        monitoringService.getSystemMetrics(),
        monitoringService.getModelMetrics(),
        monitoringService.getModelPerformance(),
        monitoringService.getResourceUtilization('cpu'),
        monitoringService.getResourceUtilization('memory'),
        monitoringService.getResourceUtilization('storage'),
        monitoringService.getResourceUtilization('network'),
      ]);

      setSystemMetrics(systemMetricsData);
      setModelMetrics(modelMetricsData);
      setModelPerformance(modelPerformanceData);
      setResourceHistory({
        cpu: cpuHistory,
        memory: memoryHistory,
        storage: storageHistory,
        network: networkHistory,
      });
    } catch (error) {
      console.error('Error loading monitoring data:', error);
    }
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      await loadData();
      setIsLoading(false);
    };
    fetchData();

    // Set up polling every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, [loadData]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadData();
    setIsRefreshing(false);
  };

  const getSystemStatus = () => {
    const thresholds = {
      cpu: 80,
      memory: 80,
      storage: 80,
      network: 80,
    };

    const isHealthy = Object.entries(thresholds).every(
      ([key, threshold]) => systemMetrics[key as keyof SystemMetrics] < threshold
    );

    return {
      label: isHealthy ? 'All Systems Operational' : 'System Warning',
      color: isHealthy ? 'success' : 'warning' as 'success' | 'warning',
      icon: isHealthy ? <CheckCircleIcon /> : <ErrorIcon />,
    };
  };

  const systemStatus = getSystemStatus();

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
              icon={systemStatus.icon}
              label={systemStatus.label}
              color={systemStatus.color}
              variant="outlined"
            />
          </Box>
        </Box>

        <Grid container spacing={3}>
          {/* Resource Utilization */}
          <Grid item xs={12}>
            <Fade in timeout={800}>
              <Box>
                <ResourceUtilizationCard
                  currentMetrics={systemMetrics}
                  historicalData={resourceHistory}
                  isLoading={isLoading}
                />
              </Box>
            </Fade>
          </Grid>

          {/* Model Performance */}
          <Grid item xs={12}>
            <Fade in timeout={800}>
              <Box>
                <ModelPerformanceCard
                  data={modelPerformance}
                  isLoading={isLoading}
                />
              </Box>
            </Fade>
          </Grid>
        </Grid>
      </Box>
    </>
  );
};

export default Monitoring;
