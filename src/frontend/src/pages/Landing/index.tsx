import { useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import {
  Box,
  Button,
  Container,
  Grid,
  Paper,
  Typography,
  useTheme,
  Fade,
  Slide,
} from '@mui/material';
import {
  Security as SecurityIcon,
  Assessment as AssessmentIcon,
  Psychology as PsychologyIcon,
  Gavel as GavelIcon,
  MonitorHeart as MonitorIcon,
  Shield as ShieldIcon,
} from '@mui/icons-material';
import { LazyLoadImage } from 'react-lazy-load-image-component';
import 'react-lazy-load-image-component/src/effects/blur.css';

const features = [
  {
    icon: <SecurityIcon sx={{ fontSize: 40 }} aria-hidden="true" />,
    title: 'Enhanced Security',
    description: 'Comprehensive security measures for AI systems with real-time monitoring and threat detection.',
  },
  {
    icon: <AssessmentIcon sx={{ fontSize: 40 }} aria-hidden="true" />,
    title: 'Performance Analytics',
    description: 'Advanced analytics and monitoring tools to track AI system performance and behavior.',
  },
  {
    icon: <PsychologyIcon sx={{ fontSize: 40 }} aria-hidden="true" />,
    title: 'AI Safety Protocols',
    description: 'Implement and monitor safety protocols to ensure responsible AI development and deployment.',
  },
  {
    icon: <GavelIcon sx={{ fontSize: 40 }} aria-hidden="true" />,
    title: 'Compliance Management',
    description: 'Stay compliant with AI regulations and industry standards through automated checks and reporting.',
  },
  {
    icon: <MonitorIcon sx={{ fontSize: 40 }} aria-hidden="true" />,
    title: 'Real-time Monitoring',
    description: 'Continuous monitoring of AI systems with instant alerts for potential issues or anomalies.',
  },
  {
    icon: <ShieldIcon sx={{ fontSize: 40 }} aria-hidden="true" />,
    title: 'Risk Management',
    description: 'Proactive risk assessment and mitigation strategies for AI deployments.',
  },
];

const Landing = () => {
  const theme = useTheme();
  const navigate = useNavigate();

  return (
    <>
      <Helmet>
        <title>AI Safety Governance Platform - Ensure Responsible AI Development</title>
        <meta name="description" content="Comprehensive AI safety monitoring and governance tools for responsible AI development and deployment." />
        <meta name="keywords" content="AI safety, governance, monitoring, compliance, security, risk management" />
      </Helmet>

      <Box component="main" role="main">
        {/* Hero Section */}
        <Box
          component="header"
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
                <Fade in timeout={1000}>
                  <Box>
                    <Typography variant="h1" sx={{ fontSize: { xs: '2.5rem', md: '3.5rem' }, mb: 2 }}>
                      AI Safety Governance Platform
                    </Typography>
                    <Typography variant="h2" sx={{ fontSize: { xs: '1.5rem', md: '2rem' }, mb: 4 }}>
                      Ensure responsible AI development with comprehensive safety monitoring and governance tools.
                    </Typography>
                    <Box sx={{ mt: 4 }}>
                      <Button
                        variant="contained"
                        color="secondary"
                        size="large"
                        onClick={() => navigate('/register')}
                        sx={{
                          mr: 2,
                          mb: { xs: 2, sm: 0 },
                          transition: 'transform 0.2s',
                          '&:hover': {
                            transform: 'scale(1.05)',
                          },
                        }}
                      >
                        Get Started
                      </Button>
                      <Button
                        variant="outlined"
                        color="inherit"
                        size="large"
                        onClick={() => navigate('/login')}
                        sx={{
                          transition: 'transform 0.2s',
                          '&:hover': {
                            transform: 'scale(1.05)',
                          },
                        }}
                      >
                        Sign In
                      </Button>
                    </Box>
                  </Box>
                </Fade>
              </Grid>
              <Grid item xs={12} md={6}>
                <Slide direction="left" in timeout={1000}>
                  <Box>
                    <LazyLoadImage
                      src="/ai-governance.svg"
                      alt="AI Governance Platform Interface showing monitoring dashboard and safety controls"
                      effect="blur"
                      style={{
                        width: '100%',
                        maxWidth: 500,
                        height: 'auto',
                        display: 'block',
                        margin: 'auto',
                      }}
                    />
                  </Box>
                </Slide>
              </Grid>
            </Grid>
          </Container>
        </Box>

        {/* Features Section */}
        <Box component="section" aria-labelledby="features-title">
          <Container maxWidth="lg" sx={{ mb: 8 }}>
            <Typography
              id="features-title"
              variant="h2"
              align="center"
              gutterBottom
              sx={{ mb: 6, fontSize: { xs: '2rem', md: '2.5rem' } }}
            >
              Key Features
            </Typography>
            <Grid container spacing={4}>
              {features.map((feature, index) => (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <Fade in timeout={1000 + index * 200}>
                    <Paper
                      elevation={2}
                      sx={{
                        p: 3,
                        height: '100%',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        textAlign: 'center',
                        transition: 'transform 0.3s, box-shadow 0.3s',
                        '&:hover': {
                          transform: 'translateY(-8px)',
                          boxShadow: theme.shadows[8],
                        },
                      }}
                    >
                      <Box
                        sx={{
                          color: theme.palette.primary.main,
                          mb: 2,
                        }}
                        aria-hidden="true"
                      >
                        {feature.icon}
                      </Box>
                      <Typography variant="h3" sx={{ fontSize: '1.5rem' }} gutterBottom>
                        {feature.title}
                      </Typography>
                      <Typography variant="body1" color="text.secondary">
                        {feature.description}
                      </Typography>
                    </Paper>
                  </Fade>
                </Grid>
              ))}
            </Grid>
          </Container>
        </Box>

        {/* Call to Action Section */}
        <Box
          component="section"
          sx={{
            bgcolor: theme.palette.grey[100],
            py: 8,
          }}
        >
          <Container maxWidth="md">
            <Fade in timeout={1000}>
              <Paper
                elevation={3}
                sx={{
                  p: 4,
                  textAlign: 'center',
                  borderRadius: 2,
                  transition: 'transform 0.3s',
                  '&:hover': {
                    transform: 'scale(1.02)',
                  },
                }}
              >
                <Typography variant="h3" sx={{ fontSize: '2rem' }} gutterBottom>
                  Ready to Enhance Your AI Safety?
                </Typography>
                <Typography variant="body1" paragraph sx={{ mb: 4 }}>
                  Join organizations worldwide in implementing robust AI safety measures.
                  Start your journey towards responsible AI development today.
                </Typography>
                <Button
                  variant="contained"
                  color="primary"
                  size="large"
                  onClick={() => navigate('/register')}
                  sx={{
                    py: 1.5,
                    px: 4,
                    transition: 'transform 0.2s',
                    '&:hover': {
                      transform: 'scale(1.05)',
                    },
                  }}
                >
                  Start Free Trial
                </Button>
              </Paper>
            </Fade>
          </Container>
        </Box>
      </Box>
    </>
  );
};

export default Landing;
