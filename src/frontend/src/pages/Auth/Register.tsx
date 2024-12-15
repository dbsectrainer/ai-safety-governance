import { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Link,
  Alert,
} from '@mui/material';
import { useSnackbar } from 'notistack';
import { authService } from '../../services/auth';
import { validationPatterns } from '../../config/security';

const Register = () => {
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    username: '',
    name: '',
  });

  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const validateField = (name: string, value: string): string => {
    switch (name) {
      case 'email':
        return !validationPatterns.email.test(value)
          ? 'Please enter a valid email address'
          : '';
      case 'password':
        return !validationPatterns.password.test(value)
          ? 'Password must contain at least 8 characters, including uppercase, lowercase, number and special character'
          : '';
      case 'confirmPassword':
        return value !== formData.password
          ? 'Passwords do not match'
          : '';
      case 'username':
        return !validationPatterns.username.test(value)
          ? 'Username must be 3-16 characters and can contain letters, numbers, underscore and hyphen'
          : '';
      case 'name':
        return !validationPatterns.name.test(value)
          ? 'Name must be 2-50 characters and can contain letters, spaces and hyphens'
          : '';
      default:
        return '';
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    
    const error = validateField(name, value);
    setValidationErrors(prev => ({
      ...prev,
      [name]: error,
    }));
    
    setError(''); // Clear general error when user types
  };

  const isFormValid = () => {
    const errors: Record<string, string> = {};
    Object.keys(formData).forEach(key => {
      const error = validateField(key, formData[key as keyof typeof formData]);
      if (error) errors[key] = error;
    });
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isFormValid()) {
      setError('Please fix the validation errors before submitting');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      // Destructure and omit confirmPassword from registration data
      const { email, password, username, name } = formData;
      await authService.register({ email, password, username, name });
      enqueueSnackbar('Registration successful! Please sign in.', { variant: 'success' });
      navigate('/login');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Registration failed';
      setError(errorMessage);
      enqueueSnackbar(errorMessage, { variant: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Typography component="h1" variant="h5" gutterBottom>
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
          }}
        >
          <Typography component="h2" variant="h5" gutterBottom>
            Create Account
          </Typography>

          {error && (
            <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              autoComplete="email"
              value={formData.email}
              onChange={handleInputChange}
              error={!!validationErrors.email}
              helperText={validationErrors.email}
              disabled={isLoading}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Username"
              name="username"
              autoComplete="username"
              value={formData.username}
              onChange={handleInputChange}
              error={!!validationErrors.username}
              helperText={validationErrors.username}
              disabled={isLoading}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              id="name"
              label="Full Name"
              name="name"
              autoComplete="name"
              value={formData.name}
              onChange={handleInputChange}
              error={!!validationErrors.name}
              helperText={validationErrors.name}
              disabled={isLoading}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="new-password"
              value={formData.password}
              onChange={handleInputChange}
              error={!!validationErrors.password}
              helperText={validationErrors.password}
              disabled={isLoading}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="confirmPassword"
              label="Confirm Password"
              type="password"
              id="confirmPassword"
              autoComplete="new-password"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              error={!!validationErrors.confirmPassword}
              helperText={validationErrors.confirmPassword}
              disabled={isLoading}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={isLoading}
            >
              {isLoading ? 'Creating Account...' : 'Create Account'}
            </Button>
          </Box>

          <Box sx={{ mt: 2 }}>
            <Link component={RouterLink} to="/login" variant="body2">
              {"Already have an account? Sign In"}
            </Link>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Register;
