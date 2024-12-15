import { useState, useCallback } from 'react';
import { useNavigate, useLocation, Link as RouterLink } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Link,
  Alert,
  InputAdornment,
  IconButton,
  CircularProgress,
  Fade,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useSnackbar } from 'notistack';
import { debounce } from 'lodash';
import { authService } from '../../services/auth';

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { enqueueSnackbar } = useSnackbar();
  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [attempts, setAttempts] = useState(0);

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/';

  const handleInputChange = useCallback(
    debounce((name: string, value: string) => {
      setFormData(prev => ({
        ...prev,
        [name]: value,
      }));
      setError('');
    }, 300),
    []
  );

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const validateForm = () => {
    if (!formData.email) {
      setError('Email is required');
      return false;
    }
    if (!/\S+@\S+\.\S+/.test(formData.email)) {
      setError('Please enter a valid email address');
      return false;
    }
    if (!formData.password) {
      setError('Password is required');
      return false;
    }
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    if (attempts >= 5) {
      setError('Too many login attempts. Please try again later.');
      enqueueSnackbar('Account temporarily locked. Please try again later.', { 
        variant: 'error',
        autoHideDuration: 5000
      });
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      await authService.login(formData);
      enqueueSnackbar('Login successful! Welcome back.', { 
        variant: 'success',
        autoHideDuration: 3000
      });
      navigate(from, { replace: true });
    } catch (err) {
      setAttempts(prev => prev + 1);
      const errorMessage = err instanceof Error 
        ? err.message 
        : 'Unable to sign in. Please check your credentials and try again.';
      setError(errorMessage);
      enqueueSnackbar(errorMessage, { 
        variant: 'error',
        autoHideDuration: 5000
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Helmet>
        <title>Sign In - AI Safety Governance Platform</title>
        <meta name="description" content="Sign in to access your AI Safety Governance Platform dashboard" />
      </Helmet>

      <Container component="main" maxWidth="xs">
        <Fade in timeout={800}>
          <Box
            sx={{
              marginTop: 8,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}
          >
            <Typography 
              component="h1" 
              variant="h4" 
              gutterBottom
              sx={{ 
                color: theme => theme.palette.primary.main,
                fontWeight: 600
              }}
            >
              AI Safety Governance Platform
            </Typography>

            <Paper
              elevation={3}
              sx={{
                padding: 4,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                width: '100%',
                borderRadius: 2,
                mt: 2,
              }}
            >
              <Typography 
                component="h2" 
                variant="h5" 
                gutterBottom
                sx={{ mb: 3 }}
              >
                Sign In
              </Typography>

              {error && (
                <Alert 
                  severity="error" 
                  sx={{ 
                    width: '100%', 
                    mb: 2,
                    '& .MuiAlert-message': {
                      width: '100%'
                    }
                  }}
                >
                  {error}
                </Alert>
              )}

              <Box 
                component="form" 
                onSubmit={handleSubmit} 
                sx={{ width: '100%' }}
                noValidate
              >
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="email"
                  label="Email Address"
                  name="email"
                  autoComplete="email"
                  autoFocus
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  disabled={isLoading}
                  InputProps={{
                    'aria-label': 'Email Address',
                  }}
                />
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  name="password"
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  autoComplete="current-password"
                  onChange={(e) => handleInputChange('password', e.target.value)}
                  disabled={isLoading}
                  InputProps={{
                    'aria-label': 'Password',
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          aria-label="toggle password visibility"
                          onClick={togglePasswordVisibility}
                          edge="end"
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  sx={{ 
                    mt: 3, 
                    mb: 2,
                    py: 1.5,
                    position: 'relative'
                  }}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <CircularProgress
                      size={24}
                      sx={{
                        position: 'absolute',
                        top: '50%',
                        left: '50%',
                        marginTop: '-12px',
                        marginLeft: '-12px',
                      }}
                    />
                  ) : (
                    'Sign In'
                  )}
                </Button>

                <Box sx={{ 
                  display: 'flex', 
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: 1
                }}>
                  <Link 
                    component={RouterLink} 
                    to="/forgot-password"
                    variant="body2"
                    sx={{ 
                      textDecoration: 'none',
                      '&:hover': {
                        textDecoration: 'underline'
                      }
                    }}
                  >
                    Forgot password?
                  </Link>
                  <Link 
                    component={RouterLink} 
                    to="/register" 
                    variant="body2"
                    sx={{ 
                      textDecoration: 'none',
                      '&:hover': {
                        textDecoration: 'underline'
                      }
                    }}
                  >
                    Don't have an account? Sign Up
                  </Link>
                </Box>
              </Box>
            </Paper>
          </Box>
        </Fade>
      </Container>
    </>
  );
};

export default Login;
