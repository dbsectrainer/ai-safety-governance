import { useState } from "react";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Link,
  Alert,
} from "@mui/material";
import { useSnackbar } from "notistack";
import { authService } from "../../services/auth";
import { validationPatterns } from "../../config/security";

const Register = () => {
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const [error, setError] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    username: "",
    full_name: "",
  });
  const [validationErrors, setValidationErrors] = useState<
    Record<string, string>
  >({});

  const validateField = (name: string, value: string): string => {
    switch (name) {
      case "email":
        return !validationPatterns.email.test(value)
          ? "Please enter a valid email address"
          : "";
      case "password":
        return !validationPatterns.password.test(value)
          ? "Password must include uppercase, lowercase, number and special character"
          : "";
      case "confirmPassword":
        return value !== formData.password ? "Passwords do not match" : "";
      case "username":
        return !validationPatterns.username.test(value)
          ? "Username must be 3-16 characters using letters, numbers, _ or -"
          : "";
      case "full_name":
        return value && !validationPatterns.name.test(value)
          ? "Full name must be 2-100 characters"
          : "";
      default:
        return "";
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    const fieldError = validateField(name, value);
    setValidationErrors((prev) => ({
      ...prev,
      [name]: fieldError,
    }));
    if (name === "password" && formData.confirmPassword) {
      setValidationErrors((prev) => ({
        ...prev,
        confirmPassword:
          formData.confirmPassword !== value ? "Passwords do not match" : "",
      }));
    }
    setError("");
  };

  const isFormValid = () => {
    const errors: Record<string, string> = {};
    Object.keys(formData).forEach((key) => {
      const fieldError = validateField(
        key,
        formData[key as keyof typeof formData],
      );
      if (fieldError) {
        errors[key] = fieldError;
      }
    });
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!isFormValid()) {
      setError("Please fix the validation errors before submitting");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const { email, password, username, full_name } = formData;
      await authService.register({ email, password, username, full_name });
      enqueueSnackbar("Registration successful! Please sign in.", {
        variant: "success",
      });
      navigate("/login");
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Registration failed";
      setError(errorMessage);
      enqueueSnackbar(errorMessage, { variant: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          marginBottom: 4,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <Typography component="h1" variant="h5" gutterBottom align="center">
          AI Safety Governance Platform
        </Typography>
        <Paper
          elevation={3}
          sx={{
            padding: { xs: 3, sm: 4 },
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            width: "100%",
          }}
        >
          <Typography component="h2" variant="h5" gutterBottom>
            Create Account
          </Typography>

          {error && (
            <Alert severity="error" sx={{ width: "100%", mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box
            component="form"
            onSubmit={handleSubmit}
            sx={{ width: "100%" }}
            noValidate
          >
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              type="email"
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
              fullWidth
              id="full_name"
              label="Full Name (optional)"
              name="full_name"
              autoComplete="name"
              value={formData.full_name}
              onChange={handleInputChange}
              error={!!validationErrors.full_name}
              helperText={validationErrors.full_name}
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
              helperText={
                validationErrors.password ||
                "At least 8 characters, including uppercase, lowercase, number and special character"
              }
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
              sx={{ mt: 3, mb: 2, py: 1.25 }}
              disabled={isLoading}
            >
              {isLoading ? "Creating Account..." : "Create Account"}
            </Button>
          </Box>

          <Box
            sx={{
              mt: 2,
              display: "flex",
              gap: 2,
              flexWrap: "wrap",
              justifyContent: "center",
            }}
          >
            <Link component={RouterLink} to="/" variant="body2">
              Back to home
            </Link>
            <Link component={RouterLink} to="/login" variant="body2">
              Already have an account? Sign In
            </Link>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Register;
