import { Navigate, useLocation } from 'react-router-dom';
import { CircularProgress, Box } from '@mui/material';
import { useState, useEffect } from 'react';
import { authService } from '../services/auth';
import type { AuthUser } from '../config/security';
import { isAdministrator } from '../config/security';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: string[];
}

const ProtectedRoute = ({ children, requiredRoles = [] }: ProtectedRouteProps) => {
  const [authState, setAuthState] = useState<{
    isLoading: boolean;
    isAuthenticated: boolean;
    user: AuthUser | null;
  }>({
    isLoading: true,
    isAuthenticated: false,
    user: null,
  });

  const location = useLocation();

  useEffect(() => {
    let cancelled = false;

    const validateAuth = async () => {
      if (!authService.isAuthenticated()) {
        if (!cancelled) {
          setAuthState({ isLoading: false, isAuthenticated: false, user: null });
        }
        return;
      }

      const user = await authService.getCurrentUser();
      if (cancelled) {
        return;
      }

      if (!user) {
        localStorage.removeItem('token');
      }
      setAuthState({
        isLoading: false,
        isAuthenticated: Boolean(user),
        user,
      });
    };

    void validateAuth();
    return () => {
      cancelled = true;
    };
  }, []);

  if (authState.isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        role="status"
        aria-label="Validating session"
      >
        <CircularProgress />
      </Box>
    );
  }

  if (!authState.isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requiredRoles.length > 0) {
    const hasRequiredRole = requiredRoles.some((role) => {
      if (role === 'admin') {
        return isAdministrator(authState.user);
      }
      return Boolean(authState.user?.roles?.includes(role));
    });

    if (!hasRequiredRole) {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return <>{children}</>;
};

export default ProtectedRoute;
