import { AxiosRequestConfig } from 'axios';

// CSRF Token handling
export const getCsrfToken = (): string => {
  return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
};

// Security headers configuration
export const securityHeaders: Record<string, string> = {
  'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';",
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'X-XSS-Protection': '1; mode=block',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
};

// Axios security configuration
export const axiosSecurityConfig: AxiosRequestConfig = {
  withCredentials: true,
  xsrfHeaderName: 'X-CSRF-Token',
  xsrfCookieName: 'csrf_token',
};

// Input validation patterns
export const validationPatterns = {
  email: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  password: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
  username: /^[a-zA-Z0-9_-]{3,16}$/,
  name: /^[a-zA-Z\s-]{2,50}$/,
};

// XSS prevention utilities
export const sanitizeInput = (input: string): string => {
  const div = document.createElement('div');
  div.textContent = input;
  return div.innerHTML;
};

export const validateInput = (input: string, pattern: RegExp): boolean => {
  return pattern.test(input);
};

// Authentication state management
export interface AuthState {
  isAuthenticated: boolean;
  user: null | {
    id: string;
    username: string;
    email: string;
    roles: string[];
  };
  token: string | null;
}

export const initialAuthState: AuthState = {
  isAuthenticated: false,
  user: null,
  token: null,
};
