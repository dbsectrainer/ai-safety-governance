import { useCallback, useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";
import {
  Alert,
  Box,
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
} from "@mui/material";
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  MonitorHeart as MonitorHeartIcon,
  Notifications as NotificationsIcon,
  People as PeopleIcon,
  Psychology as PsychologyIcon,
  Refresh as RefreshIcon,
  VerifiedUser as VerifiedUserIcon,
} from "@mui/icons-material";
import { format } from "date-fns";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
  XAxis,
  YAxis,
} from "recharts";
import { dashboardService } from "../../services/dashboard";
import type { DashboardSummary } from "../../services/dashboard";
import { getErrorMessage } from "../../services/api";
import { formatAuditAction } from "../../utils/format";

interface DashboardMetric {
  id: string;
  title: string;
  value: string | number;
  icon: JSX.Element;
  status: "success" | "warning" | "error";
}

const MetricCard = ({ metric }: { metric: DashboardMetric }) => {
  const theme = useTheme();
  const statusIcon =
    metric.status === "success" ? (
      <CheckCircleIcon color="success" fontSize="small" />
    ) : metric.status === "warning" ? (
      <ErrorIcon color="warning" fontSize="small" />
    ) : (
      <ErrorIcon color="error" fontSize="small" />
    );

  return (
    <Fade in timeout={500}>
      <Paper
        sx={{
          p: 3,
          height: "100%",
          transition: "transform 0.2s, box-shadow 0.2s",
          "&:hover": {
            transform: "translateY(-4px)",
            boxShadow: theme.shadows[8],
          },
        }}
      >
        <Box
          display="flex"
          alignItems="flex-start"
          justifyContent="space-between"
          gap={1}
          flexWrap="wrap"
        >
          <Box display="flex" alignItems="center" gap={2} sx={{ minWidth: 0 }}>
            {metric.icon}
            <Box sx={{ minWidth: 0 }}>
              <Typography variant="h6" color="text.secondary">
                {metric.title}
              </Typography>
              <Typography variant="h4" sx={{ mt: 1, overflowWrap: "anywhere" }}>
                {metric.value}
              </Typography>
            </Box>
          </Box>
          <Tooltip title={`Status: ${metric.status}`}>
            <Chip
              size="small"
              icon={statusIcon}
              label={metric.status}
              sx={{ ml: "auto" }}
            />
          </Tooltip>
        </Box>
      </Paper>
    </Fade>
  );
};

const Dashboard = () => {
  const theme = useTheme();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState("");

  const loadData = useCallback(async (background = false) => {
    if (background) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }
    try {
      const data = await dashboardService.getSummary();
      setSummary(data);
      setError("");
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

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="400px"
        role="status"
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error || !summary) {
    return (
      <Box sx={{ pb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        <Alert
          severity="error"
          action={
            <IconButton
              color="inherit"
              size="small"
              onClick={() => void loadData()}
              aria-label="Retry"
            >
              <RefreshIcon />
            </IconButton>
          }
        >
          {error || "Dashboard data is unavailable."}
        </Alert>
      </Box>
    );
  }

  const metrics: DashboardMetric[] = [
    {
      id: "users",
      title: "Active Users",
      value: summary.metrics.active_users,
      icon: (
        <PeopleIcon sx={{ fontSize: 40, color: theme.palette.primary.main }} />
      ),
      status: "success",
    },
    {
      id: "models",
      title: "Active Models",
      value: summary.metrics.active_models,
      icon: (
        <PsychologyIcon
          sx={{ fontSize: 40, color: theme.palette.primary.main }}
        />
      ),
      status: summary.metrics.active_models > 0 ? "success" : "warning",
    },
    {
      id: "compliance",
      title: "Compliance Score",
      value: summary.compliance.total
        ? `${summary.metrics.compliance_score}%`
        : "No checks yet",
      icon: (
        <VerifiedUserIcon
          sx={{ fontSize: 40, color: theme.palette.primary.main }}
        />
      ),
      status: !summary.compliance.total
        ? "warning"
        : summary.metrics.compliance_score >= 80
          ? "success"
          : summary.metrics.compliance_score >= 50
            ? "warning"
            : "error",
    },
    {
      id: "health",
      title: "System Health",
      value: summary.metrics.system_health,
      icon: (
        <MonitorHeartIcon
          sx={{ fontSize: 40, color: theme.palette.primary.main }}
        />
      ),
      status:
        summary.metrics.system_health === "Excellent"
          ? "success"
          : summary.metrics.system_health === "Critical"
            ? "error"
            : "warning",
    },
  ];

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
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          mb={4}
          gap={2}
        >
          <Typography variant="h4" component="h1">
            Dashboard
          </Typography>
          <Box>
            <Tooltip title="Refresh data">
              <IconButton
                onClick={() => void loadData(true)}
                disabled={isRefreshing}
                aria-label="Refresh dashboard"
                sx={{ mr: 1 }}
              >
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="View monitoring">
              <IconButton aria-label="View monitoring">
                <NotificationsIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        <Grid container spacing={3}>
          {metrics.map((metric) => (
            <Grid item xs={12} sm={6} lg={3} key={metric.id}>
              <MetricCard metric={metric} />
            </Grid>
          ))}

          <Grid item xs={12}>
            <Fade in timeout={500}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Platform Growth (last 24 hours)
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 2 }}
                >
                  Cumulative registered users and model versions.
                </Typography>
                <Box
                  sx={{ height: 300 }}
                  data-testid="dashboard-performance-chart"
                >
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={summary.performance}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="timestamp"
                        tickFormatter={(timestamp: number) =>
                          format(timestamp, "HH:mm")
                        }
                      />
                      <YAxis allowDecimals={false} />
                      <RechartsTooltip
                        labelFormatter={(timestamp) =>
                          typeof timestamp === "number"
                            ? format(timestamp, "MMM d, HH:mm")
                            : ""
                        }
                      />
                      <Line
                        type="monotone"
                        dataKey="users"
                        stroke={theme.palette.primary.main}
                        name="Users"
                        dot={false}
                      />
                      <Line
                        type="monotone"
                        dataKey="models"
                        stroke={theme.palette.secondary.main}
                        name="Models"
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              </Paper>
            </Fade>
          </Grid>

          <Grid item xs={12}>
            <Fade in timeout={500}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Recent Activity
                </Typography>
                {summary.activity.length === 0 ? (
                  <Typography variant="body2" color="text.secondary">
                    No recent activity recorded.
                  </Typography>
                ) : (
                  <List>
                    {summary.activity.map((log, index) => (
                      <Box key={log.id}>
                        <ListItem>
                          <ListItemIcon>
                            {log.action === "delete" ? (
                              <ErrorIcon color="error" />
                            ) : (
                              <CheckCircleIcon color="success" />
                            )}
                          </ListItemIcon>
                          <ListItemText
                            primary={formatAuditAction(log.action, log.resource_type)}
                            secondary={format(
                              new Date(log.timestamp),
                              "MMM d, yyyy HH:mm",
                            )}
                          />
                        </ListItem>
                        {index < summary.activity.length - 1 && <Divider />}
                      </Box>
                    ))}
                  </List>
                )}
              </Paper>
            </Fade>
          </Grid>
        </Grid>
      </Box>
    </>
  );
};

export default Dashboard;
