import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  Grid,
  Paper,
  Typography,
  useTheme,
} from '@mui/material';
import {
  Security as SecurityIcon,
  Assessment as AssessmentIcon,
  Psychology as PsychologyIcon,
  Gavel as GavelIcon,
  MonitorHeart as MonitorIcon,
  Shield as ShieldIcon,
} from '@mui/icons-material';

const features = [
  {
    icon: <SecurityIcon sx={{ fontSize: 40 }} />,
    title: 'Enhanced Security',
    description: 'Comprehensive security measures for AI systems with real-time monitoring and threat detection.',
  },
  {
    icon: <AssessmentIcon sx={{ fontSize: 40 }} />,
    title: 'Performance Analytics',
    description: 'Advanced analytics and monitoring tools to track AI system performance and behavior.',
  },
  {
    icon: <PsychologyIcon sx={{ fontSize: 40 }} />,
    title: 'AI Safety Protocols',
    description: 'Implement and monitor safety protocols to ensure responsible AI development and deployment.',
  },
  {
    icon: <GavelIcon sx={{ fontSize: 40 }} />,
    title: 'Compliance Management',
    description: 'Stay compliant with AI regulations and industry standards through automated checks and reporting.',
  },
  {
    icon: <MonitorIcon sx={{ fontSize: 40 }} />,
    title: 'Real-time Monitoring',
    description: 'Continuous monitoring of AI systems with instant alerts for potential issues or anomalies.',
  },
  {
    icon: <ShieldIcon sx={{ fontSize: 40 }} />,
    title: 'Risk Management',
    description: 'Proactive risk assessment and mitigation strategies for AI deployments.',
  },
];

const Landing = () => {
  const theme = useTheme();
  const navigate = useNavigate();

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          bgcolor: theme.palette.primary.main,
          color: 'white',
          py: 8,
          mb: 6,
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography variant="h2" component="h1" gutterBottom>
                AI Safety Governance Platform
              </Typography>
              <Typography variant="h5" paragraph>
                Ensure responsible AI development with comprehensive safety monitoring and governance tools.
              </Typography>
              <Box sx={{ mt: 4 }}>
                <Button
                  variant="contained"
                  color="secondary"
                  size="large"
                  onClick={() => navigate('/register')}
                  sx={{ mr: 2 }}
                >
                  Get Started
                </Button>
                <Button
                  variant="outlined"
                  color="inherit"
                  size="large"
                  onClick={() => navigate('/login')}
                >
                  Sign In
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box
                component="img"
                src="/ai-governance.svg"
                alt="AI Governance"
                sx={{
                  width: '100%',
                  maxWidth: 500,
                  height: 'auto',
                  display: 'block',
                  margin: 'auto',
                }}
              />
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ mb: 8 }}>
        <Typography
          variant="h3"
          component="h2"
          align="center"
          gutterBottom
          sx={{ mb: 6 }}
        >
          Key Features
        </Typography>
        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Paper
                elevation={2}
                sx={{
                  p: 3,
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  textAlign: 'center',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                  },
                }}
              >
                <Box
                  sx={{
                    color: theme.palette.primary.main,
                    mb: 2,
                  }}
                >
                  {feature.icon}
                </Box>
                <Typography variant="h6" gutterBottom>
                  {feature.title}
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  {feature.description}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Call to Action Section */}
      <Box
        sx={{
          bgcolor: theme.palette.grey[100],
          py: 8,
        }}
      >
        <Container maxWidth="md">
          <Paper
            elevation={3}
            sx={{
              p: 4,
              textAlign: 'center',
              borderRadius: 2,
            }}
          >
            <Typography variant="h4" gutterBottom>
              Ready to Enhance Your AI Safety?
            </Typography>
            <Typography variant="body1" paragraph sx={{ mb: 4 }}>
              Join organizations worldwide in implementing robust AI safety measures.
              Get started with our comprehensive governance platform today.
            </Typography>
            <Button
              variant="contained"
              color="primary"
              size="large"
              onClick={() => navigate('/register')}
            >
              Start Free Trial
            </Button>
          </Paper>
        </Container>
      </Box>
    </Box>
  );
};

export default Landing;
