import { Box, Typography, Paper, Grid, Chip, LinearProgress } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';

interface ComplianceMetric {
  name: string;
  score: number;
  status: 'compliant' | 'warning' | 'violation';
}

const complianceMetrics: ComplianceMetric[] = [
  { name: 'Data Privacy', score: 95, status: 'compliant' },
  { name: 'Model Fairness', score: 88, status: 'warning' },
  { name: 'Security Controls', score: 98, status: 'compliant' },
  { name: 'Documentation', score: 92, status: 'compliant' },
  { name: 'Access Control', score: 85, status: 'warning' },
];

const ComplianceMetricCard = ({ metric }: { metric: ComplianceMetric }) => {
  const getStatusColor = (status: string): 'success' | 'warning' | 'error' => {
    switch (status) {
      case 'compliant':
        return 'success';
      case 'warning':
        return 'warning';
      case 'violation':
        return 'error';
      default:
        return 'error';
    }
  };

  const color = getStatusColor(metric.status);

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">{metric.name}</Typography>
        <Chip
          icon={metric.status === 'compliant' ? <CheckCircleIcon /> : <WarningIcon />}
          label={metric.status.charAt(0).toUpperCase() + metric.status.slice(1)}
          color={color}
          size="small"
        />
      </Box>
      <Box display="flex" alignItems="center" gap={1}>
        <LinearProgress
          variant="determinate"
          value={metric.score}
          sx={{ flexGrow: 1 }}
          color={color}
        />
        <Typography variant="body2" color="text.secondary">
          {metric.score}%
        </Typography>
      </Box>
    </Paper>
  );
};

const Compliance = () => {
  const overallScore = Math.round(
    complianceMetrics.reduce((acc, curr) => acc + curr.score, 0) / complianceMetrics.length
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Compliance Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Overall Compliance Score */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>
              Overall Compliance Score
            </Typography>
            <Typography variant="h2" color="primary">
              {overallScore}%
            </Typography>
            <LinearProgress
              variant="determinate"
              value={overallScore}
              sx={{ mt: 2, height: 10, borderRadius: 5 }}
              color="primary"
            />
          </Paper>
        </Grid>

        {/* Individual Metrics */}
        {complianceMetrics.map((metric) => (
          <Grid item xs={12} md={6} key={metric.name}>
            <ComplianceMetricCard metric={metric} />
          </Grid>
        ))}

        {/* Compliance Actions */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Compliance Activities
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • Automated compliance scan completed - 2 hours ago
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • Model fairness assessment updated - 6 hours ago
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • Access control audit completed - 1 day ago
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Compliance;
