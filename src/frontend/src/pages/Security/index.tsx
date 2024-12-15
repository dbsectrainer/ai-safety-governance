import { Box, Typography, Grid, Paper } from '@mui/material';
import {
  Shield as ShieldIcon,
  Lock as LockIcon,
  VpnKey as VpnKeyIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';

interface SecurityMetric {
  title: string;
  value: string;
  icon: JSX.Element;
  description: string;
}

const securityMetrics: SecurityMetric[] = [
  {
    title: 'Security Score',
    value: '95%',
    icon: <ShieldIcon color="primary" sx={{ fontSize: 40 }} />,
    description: 'Overall platform security rating',
  },
  {
    title: 'Active Sessions',
    value: '24',
    icon: <LockIcon color="primary" sx={{ fontSize: 40 }} />,
    description: 'Current authenticated user sessions',
  },
  {
    title: 'Access Policies',
    value: '12',
    icon: <VpnKeyIcon color="primary" sx={{ fontSize: 40 }} />,
    description: 'Active security policies',
  },
  {
    title: 'Security Events',
    value: '0',
    icon: <SecurityIcon color="primary" sx={{ fontSize: 40 }} />,
    description: 'Security incidents in last 24h',
  },
];

const SecurityMetricCard = ({ metric }: { metric: SecurityMetric }) => (
  <Paper sx={{ p: 3, height: '100%' }}>
    <Box display="flex" alignItems="center" gap={2} mb={2}>
      {metric.icon}
      <Box>
        <Typography variant="h6" gutterBottom>
          {metric.title}
        </Typography>
        <Typography variant="h4" color="primary">
          {metric.value}
        </Typography>
      </Box>
    </Box>
    <Typography variant="body2" color="text.secondary">
      {metric.description}
    </Typography>
  </Paper>
);

const Security = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Security Overview
      </Typography>

      <Grid container spacing={3}>
        {securityMetrics.map((metric) => (
          <Grid item xs={12} md={6} lg={3} key={metric.title}>
            <SecurityMetricCard metric={metric} />
          </Grid>
        ))}

        {/* Recent Security Events */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Security Events
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                • Failed login attempt detected - 3 hours ago
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                • Security policy updated - 6 hours ago
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                • Access permissions modified - 12 hours ago
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • System security scan completed - 1 day ago
              </Typography>
            </Box>
          </Paper>
        </Grid>

        {/* Security Recommendations */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Security Recommendations
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                • Enable two-factor authentication for all admin accounts
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                • Review and update access policies
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                • Schedule regular security audits
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Update security monitoring configurations
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Security;
