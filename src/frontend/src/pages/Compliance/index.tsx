import { useCallback, useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";
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
  LinearProgress,
  Paper,
  Tooltip,
  Typography,
  useTheme,
} from "@mui/material";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import WarningIcon from "@mui/icons-material/Warning";
import ErrorIcon from "@mui/icons-material/Error";
import InfoIcon from "@mui/icons-material/Info";
import RefreshIcon from "@mui/icons-material/Refresh";
import DownloadIcon from "@mui/icons-material/Download";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import { format } from "date-fns";
import { useSnackbar } from "notistack";
import { complianceService } from "../../services/compliance";
import type {
  AuditLogEntry,
  ComplianceRecord,
  ComplianceSummary,
} from "../../services/compliance";
import { getErrorMessage } from "../../services/api";

const statusLabel = (status: string) => {
  switch (status) {
    case "compliant":
      return "Compliant";
    case "non_compliant":
      return "Non-compliant";
    case "needs_review":
      return "Needs review";
    default:
      return status;
  }
};

const statusColor = (status: string): "success" | "warning" | "error" => {
  if (status === "compliant") return "success";
  if (status === "needs_review") return "warning";
  return "error";
};

const scoreForStatus = (status: string) =>
  status === "compliant" ? 100 : status === "needs_review" ? 50 : 0;

const statusIcon = (status: string) => {
  if (status === "compliant") return <CheckCircleIcon />;
  if (status === "needs_review") return <WarningIcon />;
  return <ErrorIcon />;
};

const descriptionFor = (record: ComplianceRecord) => {
  const description = record.details?.description;
  return typeof description === "string"
    ? description
    : "Compliance configuration check";
};

const ComplianceMetricCard = ({ record }: { record: ComplianceRecord }) => {
  const theme = useTheme();
  const score = scoreForStatus(record.status);
  const color = statusColor(record.status);

  return (
    <Fade in timeout={400}>
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
          justifyContent="space-between"
          alignItems="center"
          mb={2}
          gap={1}
        >
          <Box display="flex" alignItems="center" gap={1}>
            <Typography variant="h6">{record.regulation_type}</Typography>
            <Tooltip title={descriptionFor(record)} arrow>
              <IconButton
                size="small"
                aria-label={`About ${record.regulation_type}`}
              >
                <InfoIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
          <Chip
            icon={statusIcon(record.status)}
            label={statusLabel(record.status)}
            color={color}
            size="small"
          />
        </Box>
        <Box display="flex" alignItems="center" gap={1}>
          <LinearProgress
            variant="determinate"
            value={score}
            sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
            color={color}
          />
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ minWidth: "45px" }}
          >
            {score}%
          </Typography>
        </Box>
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ mt: 1, display: "block" }}
        >
          Checked: {format(new Date(record.created_at), "MMM d, yyyy HH:mm")}
        </Typography>
        {record.next_review_date && (
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ display: "block" }}
          >
            Next review:{" "}
            {format(new Date(record.next_review_date), "MMM d, yyyy")}
          </Typography>
        )}
      </Paper>
    </Fade>
  );
};

const Compliance = () => {
  const theme = useTheme();
  const { enqueueSnackbar } = useSnackbar();
  const [summary, setSummary] = useState<ComplianceSummary | null>(null);
  const [records, setRecords] = useState<ComplianceRecord[]>([]);
  const [activities, setActivities] = useState<AuditLogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState("");

  const loadData = useCallback(async (background = false) => {
    if (background) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }
    try {
      const [summaryData, recordsData, logs] = await Promise.all([
        complianceService.getSummary(),
        complianceService.getRecords(),
        complianceService.getAuditLogs(),
      ]);
      setSummary(summaryData);
      setRecords(recordsData);
      setActivities(logs.slice(0, 8));
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

  const handleRunChecks = async () => {
    setIsRunning(true);
    try {
      const result = await complianceService.runChecks();
      enqueueSnackbar(
        `Compliance checks complete: ${result.summary.compliant_rules}/${result.summary.total_rules} compliant`,
        {
          variant:
            result.summary.compliant_rules === result.summary.total_rules
              ? "success"
              : "warning",
        },
      );
      await loadData(true);
    } catch (err) {
      enqueueSnackbar(getErrorMessage(err), { variant: "error" });
    } finally {
      setIsRunning(false);
    }
  };

  const handleExportReport = () => {
    const report = {
      generated_at: new Date().toISOString(),
      summary,
      records,
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `compliance-report-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    enqueueSnackbar("Compliance report downloaded", { variant: "success" });
  };

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

  const latest = summary?.latest ?? [];
  const score = summary?.score ?? 0;
  const total = summary?.total_regulations ?? 0;
  const counts = summary?.status_counts ?? {};

  return (
    <>
      <Helmet>
        <title>Compliance Dashboard - AI Safety Governance Platform</title>
        <meta
          name="description"
          content="Monitor and manage AI system compliance with regulatory requirements and safety standards"
        />
      </Helmet>

      <Box sx={{ pb: 4 }}>
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          mb={3}
          gap={2}
        >
          <Typography variant="h4" component="h1">
            Compliance Dashboard
          </Typography>
          <Box display="flex" alignItems="center" gap={1} flexWrap="wrap">
            <Tooltip title="Refresh data">
              <IconButton
                onClick={() => void loadData(true)}
                disabled={isRefreshing}
                aria-label="Refresh compliance data"
              >
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={handleExportReport}
              disabled={records.length === 0}
            >
              Export Report
            </Button>
            <Button
              variant="contained"
              startIcon={
                isRunning ? (
                  <CircularProgress size={16} color="inherit" />
                ) : (
                  <PlayArrowIcon />
                )
              }
              onClick={() => void handleRunChecks()}
              disabled={isRunning}
            >
              {isRunning ? "Running..." : "Run Checks"}
            </Button>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Alert severity="info" sx={{ mb: 3 }}>
          Checks validate platform configuration against declared regulatory
          thresholds. They are an audit aid, not a legal certification.
        </Alert>

        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Fade in timeout={400}>
              <Paper sx={{ p: 4, textAlign: "center" }}>
                <Typography variant="h6" gutterBottom>
                  Overall Compliance Score
                </Typography>
                <Typography
                  variant="h2"
                  color={theme.palette.primary.main}
                  sx={{ mb: 2 }}
                >
                  {total ? `${score}%` : "No checks yet"}
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={total ? score : 0}
                  sx={{ height: 10, borderRadius: 5, mb: 1 }}
                  color={
                    score >= 80 ? "success" : score >= 50 ? "warning" : "error"
                  }
                />
                <Typography variant="body2" color="text.secondary">
                  Based on {total} regulation{total === 1 ? "" : "s"} ·{" "}
                  {counts.compliant ?? 0} compliant ·{" "}
                  {counts.non_compliant ?? 0} non-compliant ·{" "}
                  {counts.needs_review ?? 0} needs review
                </Typography>
                {summary?.last_run && (
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{ display: "block", mt: 1 }}
                  >
                    Last run:{" "}
                    {format(new Date(summary.last_run), "MMM d, yyyy HH:mm")}
                  </Typography>
                )}
                {total === 0 && (
                  <Button
                    sx={{ mt: 2 }}
                    variant="contained"
                    startIcon={<PlayArrowIcon />}
                    onClick={() => void handleRunChecks()}
                    disabled={isRunning}
                  >
                    Run the first compliance check
                  </Button>
                )}
              </Paper>
            </Fade>
          </Grid>

          {latest.length === 0 ? (
            <Grid item xs={12}>
              <Paper sx={{ p: 4, textAlign: "center" }}>
                <Typography variant="h6" gutterBottom>
                  No compliance records yet
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Run the configured checks to create a compliance snapshot for
                  GDPR, HIPAA and CCPA.
                </Typography>
              </Paper>
            </Grid>
          ) : (
            latest.map((record) => (
              <Grid item xs={12} md={6} key={record.regulation_type}>
                <ComplianceMetricCard record={record} />
              </Grid>
            ))
          )}

          <Grid item xs={12}>
            <Fade in timeout={400}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Recent Compliance Activity
                </Typography>
                {activities.length === 0 ? (
                  <Typography variant="body2" color="text.secondary">
                    No audit entries recorded.
                  </Typography>
                ) : (
                  activities.map((activity, index) => (
                    <Box key={activity.id}>
                      <Box sx={{ py: 1 }}>
                        <Typography variant="body2" color="text.primary">
                          {activity.action.replace("_", " ")} ·{" "}
                          {activity.resource_type.replace("_", " ")}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {format(
                            new Date(activity.timestamp),
                            "MMM d, yyyy HH:mm",
                          )}
                        </Typography>
                      </Box>
                      {index < activities.length - 1 && <Divider />}
                    </Box>
                  ))
                )}
              </Paper>
            </Fade>
          </Grid>
        </Grid>
      </Box>
    </>
  );
};

export default Compliance;
