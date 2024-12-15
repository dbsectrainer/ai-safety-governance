import { Navigate, useLocation } from 'react-router-dom';
import { CircularProgress, Box } from '@mui/material';
import { useState, useEffect } from 'react';
import { authService } from '../services/auth';
import { AuthState } from '../config/security';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: string[];
}

const ProtectedRoute = ({ children, requiredRoles = [] }: ProtectedRouteProps) => {
  const [authState, setAuthState] = useState<{
    isLoading: boolean;
    isAuthenticated: boolean;
    user: AuthState['user'];
  }>({
    isLoading: true,
    isAuthenticated: false,
    user: null,
  });

  const location = useLocation();

  useEffect(() => {
    const validateAuth = async () => {
      try {
        if (!authService.isAuthenticated()) {
          setAuthState({
            isLoading: false,
            isAuthenticated: false,
            user: null,
          });
          return;
        }

        const user = await authService.getCurrentUser();
        setAuthState({
          isLoading: false,
          isAuthenticated: !!user,
          user,
        });
      } catch {
        console.error('Authentication validation failed');
        setAuthState({
          isLoading: false,
          isAuthenticated: false,
          user: null,
        });
      }
    };

    validateAuth();
  }, []);

  if (authState.isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  if (!authState.isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check role-based access if required
  if (requiredRoles.length > 0 && authState.user) {
    const hasRequiredRole = requiredRoles.some(role => 
      authState.user?.roles.includes(role)
    );

    if (!hasRequiredRole) {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return <>{children}</>;
};

export default ProtectedRoute;
