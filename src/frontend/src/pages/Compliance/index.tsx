import { useState, useEffect } from 'react';
import { Helmet } from 'react-helmet-async';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  LinearProgress,
  Button,
  Tooltip,
  IconButton,
  Fade,
  CircularProgress,
  useTheme,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';
import InfoIcon from '@mui/icons-material/Info';
import RefreshIcon from '@mui/icons-material/Refresh';
import DownloadIcon from '@mui/icons-material/Download';
import { format } from 'date-fns';

interface ComplianceMetric {
  id: string;
  name: string;
  score: number;
  status: 'compliant' | 'warning' | 'violation';
  lastUpdated: Date;
  description: string;
}

interface ComplianceActivity {
  id: string;
  description: string;
  timestamp: Date;
  type: 'scan' | 'assessment' | 'audit' | 'update';
}

const mockComplianceMetrics: ComplianceMetric[] = [
  {
    id: '1',
    name: 'Data Privacy',
    score: 95,
    status: 'compliant',
    lastUpdated: new Date(),
    description: 'Measures compliance with data protection regulations and privacy standards',
  },
  {
    id: '2',
    name: 'Model Fairness',
    score: 88,
    status: 'warning',
    lastUpdated: new Date(),
    description: 'Evaluates AI model bias and fairness across different demographic groups',
  },
  {
    id: '3',
    name: 'Security Controls',
    score: 98,
    status: 'compliant',
    lastUpdated: new Date(),
    description: 'Assesses implementation of security measures and access controls',
  },
  {
    id: '4',
    name: 'Documentation',
    score: 92,
    status: 'compliant',
    lastUpdated: new Date(),
    description: 'Tracks completeness and quality of system documentation',
  },
  {
    id: '5',
    name: 'Access Control',
    score: 85,
    status: 'warning',
    lastUpdated: new Date(),
    description: 'Monitors user access patterns and permission management',
  },
];

const mockActivities: ComplianceActivity[] = [
  {
    id: '1',
    description: 'Automated compliance scan completed',
    timestamp: new Date(),
    type: 'scan',
  },
  {
    id: '2',
    description: 'Model fairness assessment updated',
    timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000),
    type: 'assessment',
  },
  {
    id: '3',
    description: 'Access control audit completed',
    timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000),
    type: 'audit',
  },
];

const ComplianceMetricCard = ({ metric }: { metric: ComplianceMetric }) => {
  const theme = useTheme();

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

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'compliant':
        return <CheckCircleIcon />;
      case 'warning':
        return <WarningIcon />;
      case 'violation':
        return <ErrorIcon />;
      default:
        return <ErrorIcon />;
    }
  };

  const color = getStatusColor(metric.status);

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
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            <Typography variant="h6">{metric.name}</Typography>
            <Tooltip title={metric.description} arrow>
              <IconButton size="small">
                <InfoIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
          <Chip
            icon={getStatusIcon(metric.status)}
            label={metric.status.charAt(0).toUpperCase() + metric.status.slice(1)}
            color={color}
            size="small"
          />
        </Box>
        <Box display="flex" alignItems="center" gap={1}>
          <LinearProgress
            variant="determinate"
            value={metric.score}
            sx={{
              flexGrow: 1,
              height: 8,
              borderRadius: 4,
            }}
            color={color}
          />
          <Typography variant="body2" color="text.secondary" sx={{ minWidth: '45px' }}>
            {metric.score}%
          </Typography>
        </Box>
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          Last updated: {format(metric.lastUpdated, 'MMM d, yyyy HH:mm')}
        </Typography>
      </Paper>
    </Fade>
  );
};

const Compliance = () => {
  const theme = useTheme();
  const [metrics, setMetrics] = useState<ComplianceMetric[]>([]);
  const [activities, setActivities] = useState<ComplianceActivity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const overallScore = Math.round(
    metrics.reduce((acc, curr) => acc + curr.score, 0) / metrics.length
  );

  useEffect(() => {
    // Simulate API call
    const loadData = async () => {
      setIsLoading(true);
      try {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        setMetrics(mockComplianceMetrics);
        setActivities(mockActivities);
      } catch (error) {
        console.error('Error loading compliance data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      setMetrics(mockComplianceMetrics);
      setActivities(mockActivities);
    } catch (error) {
      console.error('Error refreshing compliance data:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleExportReport = () => {
    // Implementation for exporting compliance report
    console.log('Exporting compliance report...');
  };

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="400px"
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <>
      <Helmet>
        <title>Compliance Dashboard - AI Safety Governance Platform</title>
        <meta name="description" content="Monitor and manage AI system compliance with regulatory requirements and safety standards" />
      </Helmet>

      <Box sx={{ pb: 4 }}>
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          mb={4}
        >
          <Typography variant="h4" component="h1">
            Compliance Dashboard
          </Typography>
          <Box>
            <Tooltip title="Refresh data">
              <IconButton
                onClick={handleRefresh}
                disabled={isRefreshing}
                sx={{ mr: 1 }}
              >
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Button
              variant="contained"
              startIcon={<DownloadIcon />}
              onClick={handleExportReport}
            >
              Export Report
            </Button>
          </Box>
        </Box>

        <Grid container spacing={3}>
          {/* Overall Compliance Score */}
          <Grid item xs={12}>
            <Fade in timeout={800}>
              <Paper
                sx={{
                  p: 4,
                  textAlign: 'center',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                  },
                }}
              >
                <Typography variant="h6" gutterBottom>
                  Overall Compliance Score
                </Typography>
                <Typography
                  variant="h2"
                  color={theme.palette.primary.main}
                  sx={{ mb: 2 }}
                >
                  {overallScore}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={overallScore}
                  sx={{
                    height: 10,
                    borderRadius: 5,
                    mb: 1,
                  }}
                  color="primary"
                />
                <Typography variant="body2" color="text.secondary">
                  Based on {metrics.length} compliance metrics
                </Typography>
              </Paper>
            </Fade>
          </Grid>

          {/* Individual Metrics */}
          {metrics.map((metric) => (
            <Grid item xs={12} md={6} key={metric.id}>
              <ComplianceMetricCard metric={metric} />
            </Grid>
          ))}

          {/* Compliance Activities */}
          <Grid item xs={12}>
            <Fade in timeout={800}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Recent Compliance Activities
                </Typography>
                {activities.map((activity) => (
                  <Box
                    key={activity.id}
                    sx={{
                      py: 1,
                      borderBottom: `1px solid ${theme.palette.divider}`,
                      '&:last-child': {
                        borderBottom: 'none',
                      },
                    }}
                  >
                    <Typography variant="body2" color="text.primary">
                      {activity.description}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {format(activity.timestamp, 'MMM d, yyyy HH:mm')}
                    </Typography>
                  </Box>
                ))}
              </Paper>
            </Fade>
          </Grid>
        </Grid>
      </Box>
    </>
  );
};

export default Compliance;
