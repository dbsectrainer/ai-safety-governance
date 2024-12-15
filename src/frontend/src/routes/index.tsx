import { Routes, Route, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import { CircularProgress, Box } from '@mui/material';
import ProtectedRoute from '../components/ProtectedRoute';

// Lazy load components for better initial load performance
const Dashboard = lazy(() => import('../pages/Dashboard'));
const Users = lazy(() => import('../pages/Users'));
const Config = lazy(() => import('../pages/Config'));
const Monitoring = lazy(() => import('../pages/Monitoring'));
const Compliance = lazy(() => import('../pages/Compliance'));
const Security = lazy(() => import('../pages/Security'));
const Login = lazy(() => import('../pages/Auth/Login'));
const Register = lazy(() => import('../pages/Auth/Register'));
const Unauthorized = lazy(() => import('../pages/Auth/Unauthorized'));

const LoadingFallback = () => (
  <Box 
    display="flex" 
    justifyContent="center" 
    alignItems="center" 
    height="100vh"
  >
    <CircularProgress />
  </Box>
);

const AppRoutes = () => {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/unauthorized" element={<Unauthorized />} />

        {/* Protected Routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/users"
          element={
            <ProtectedRoute requiredRoles={['admin']}>
              <Users />
            </ProtectedRoute>
          }
        />
        <Route
          path="/config"
          element={
            <ProtectedRoute requiredRoles={['admin']}>
              <Config />
            </ProtectedRoute>
          }
        />
        <Route
          path="/monitoring"
          element={
            <ProtectedRoute>
              <Monitoring />
            </ProtectedRoute>
          }
        />
        <Route
          path="/compliance"
          element={
            <ProtectedRoute requiredRoles={['admin', 'compliance-officer']}>
              <Compliance />
            </ProtectedRoute>
          }
        />
        <Route
          path="/security"
          element={
            <ProtectedRoute requiredRoles={['admin', 'security-officer']}>
              <Security />
            </ProtectedRoute>
          }
        />

        {/* Fallback route */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
};

export default AppRoutes;
