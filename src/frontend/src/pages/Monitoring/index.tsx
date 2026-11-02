import { useCallback, useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";
import {
  Alert,
  Box,
  Chip,
  Fade,
  Grid,
  IconButton,
  Paper,
  Tooltip,
  Typography,
} from "@mui/material";
import RefreshIcon from "@mui/icons-material/Refresh";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";
import SettingsIcon from "@mui/icons-material/Settings";
import { useNavigate } from "react-router-dom";
import { monitoringService } from "../../services/monitoring";
import type {
  MetricData,
  ModelMetrics,
  ModelPerformance,
  MonitoringAlert,
  SystemMetrics,
} from "../../services/monitoring";
import { getErrorMessage } from "../../services/api";
import ModelPerformanceCard from "../../components/Monitoring/ModelPerformanceCard";
import ResourceUtilizationCard from "../../components/Monitoring/ResourceUtilizationCard";

interface ResourceHistoricalData {
  [key: string]: MetricData[];
}

const initialSystemMetrics: SystemMetrics = {
  cpu: 0,
  memory: 0,
  storage: 0,
  network: 0,
};
const initialModelMetrics: ModelMetrics = {
  activeModels: 0,
  responseTime: 0,
  errorRate: 0,
  requestsPerMinute: 0,
  accuracy: 0,
  latency: 0,
  throughput: 0,
};

const Monitoring = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [systemMetrics, setSystemMetrics] =
    useState<SystemMetrics>(initialSystemMetrics);
  const [modelMetrics, setModelMetrics] =
    useState<ModelMetrics>(initialModelMetrics);
  const [modelPerformance, setModelPerformance] = useState<ModelPerformance[]>(
    [],
  );
  const [resourceHistory, setResourceHistory] =
    useState<ResourceHistoricalData>({});
  const [alerts, setAlerts] = useState<MonitoringAlert[]>([]);
  const [error, setError] = useState("");

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
        alertData,
      ] = await Promise.all([
        monitoringService.getSystemMetrics(),
        monitoringService.getModelMetrics(),
        monitoringService.getModelPerformance(),
        monitoringService.getResourceUtilization("cpu"),
        monitoringService.getResourceUtilization("memory"),
        monitoringService.getResourceUtilization("storage"),
        monitoringService.getResourceUtilization("network"),
        monitoringService.getAlerts(),
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
      setAlerts(alertData);
      setError("");
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    const fetchData = async () => {
      setIsLoading(true);
      await loadData();
      if (!cancelled) {
        setIsLoading(false);
      }
    };
    void fetchData();

    const interval = setInterval(() => {
      void loadData();
    }, 30000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [loadData]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadData();
    setIsRefreshing(false);
  };

  const thresholds = { cpu: 80, memory: 80, storage: 80, network: 80 };
  const isHealthy = Object.entries(thresholds).every(
    ([key, threshold]) => systemMetrics[key as keyof SystemMetrics] < threshold,
  );

  const stats = [
    { label: "Active Models", value: modelMetrics.activeModels },
    {
      label: "Accuracy",
      value: modelMetrics.accuracy
        ? `${(modelMetrics.accuracy * 100).toFixed(1)}%`
        : "No data",
    },
    {
      label: "Avg Latency",
      value: modelMetrics.latency
        ? `${modelMetrics.latency.toFixed(1)} ms`
        : "No data",
    },
    {
      label: "Error Rate",
      value: modelMetrics.errorRate
        ? `${(modelMetrics.errorRate * 100).toFixed(1)}%`
        : "No data",
    },
  ];

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
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          mb={3}
          gap={2}
          flexWrap="wrap"
        >
          <Typography variant="h4" component="h1">
            System Monitoring
          </Typography>
          <Box display="flex" alignItems="center" gap={1} flexWrap="wrap">
            <Tooltip title="Refresh data">
              <IconButton
                onClick={() => void handleRefresh()}
                disabled={isRefreshing}
                aria-label="Refresh monitoring data"
              >
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Configure monitoring settings">
              <IconButton
                aria-label="Configure monitoring settings"
                onClick={() => navigate("/config")}
              >
                <SettingsIcon />
              </IconButton>
            </Tooltip>
            <Chip
              icon={isHealthy ? <CheckCircleIcon /> : <ErrorIcon />}
              label={isHealthy ? "All Systems Operational" : "System Warning"}
              color={isHealthy ? "success" : "warning"}
              variant="outlined"
            />
            {alerts.length > 0 && (
              <Chip
                label={`${alerts.length} alert${alerts.length === 1 ? "" : "s"}`}
                color="warning"
              />
            )}
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          {stats.map((stat) => (
            <Grid item xs={6} md={3} key={stat.label}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  {stat.label}
                </Typography>
                <Typography variant="h5" sx={{ mt: 1 }}>
                  {stat.value}
                </Typography>
              </Paper>
            </Grid>
          ))}

          <Grid item xs={12}>
            <Fade in timeout={400}>
              <Box>
                <ResourceUtilizationCard
                  currentMetrics={systemMetrics}
                  historicalData={resourceHistory}
                  isLoading={isLoading}
                />
              </Box>
            </Fade>
          </Grid>

          <Grid item xs={12}>
            <Fade in timeout={400}>
              <Box>
                <ModelPerformanceCard
                  data={modelPerformance}
                  isLoading={isLoading}
                />
              </Box>
            </Fade>
          </Grid>

          {alerts.length > 0 && (
            <Grid item xs={12}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Active Alerts
                </Typography>
                {alerts.map((alert) => (
                  <Alert
                    key={alert.id}
                    severity={alert.severity === "high" ? "error" : "warning"}
                    sx={{ mb: 1 }}
                  >
                    {alert.message}
                  </Alert>
                ))}
              </Paper>
            </Grid>
          )}
        </Grid>
      </Box>
    </>
  );
};

export default Monitoring;
