import axios, { AxiosError } from 'axios';
import { axiosSecurityConfig, AuthState, validationPatterns } from '../config/security';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with security configurations
const authApi = axios.create({
  baseURL: `${API_URL}/auth`,
  ...axiosSecurityConfig,
});

// Add request interceptor for token handling
authApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

interface ApiErrorResponse {
  message: string;
  status: number;
}

// Add response interceptor for token refresh
authApi.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await authApi.post('/refresh', { refreshToken });
        const { token } = response.data;
        localStorage.setItem('token', token);
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return authApi(originalRequest);
      } catch (error) {
        // Handle refresh token failure
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(error);
      }
    }
    return Promise.reject(error);
  }
);

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData extends LoginCredentials {
  username: string;
  name: string;
}

interface LoginResponse {
  token: string;
  refreshToken: string;
  user: AuthState['user'];
}

class AuthService {
  private validateEmail(email: string): boolean {
    return validationPatterns.email.test(email);
  }

  private validatePassword(password: string): boolean {
    return validationPatterns.password.test(password);
  }

  async login(credentials: LoginCredentials): Promise<AuthState> {
    if (!this.validateEmail(credentials.email)) {
      throw new Error('Invalid email format');
    }

    if (!this.validatePassword(credentials.password)) {
      throw new Error('Invalid password format');
    }

    try {
      const response = await authApi.post<LoginResponse>('/login', credentials);
      const { token, refreshToken, user } = response.data;
      
      localStorage.setItem('token', token);
      localStorage.setItem('refreshToken', refreshToken);

      return {
        isAuthenticated: true,
        user,
        token,
      };
    } catch (error) {
      const axiosError = error as AxiosError<ApiErrorResponse>;
      throw new Error(
        axiosError.response?.data?.message || 
        'Login failed. Please check your credentials and try again.'
      );
    }
  }

  async register(data: RegisterData): Promise<void> {
    if (!this.validateEmail(data.email)) {
      throw new Error('Invalid email format');
    }

    if (!this.validatePassword(data.password)) {
      throw new Error('Invalid password format');
    }

    if (!validationPatterns.username.test(data.username)) {
      throw new Error('Invalid username format');
    }

    if (!validationPatterns.name.test(data.name)) {
      throw new Error('Invalid name format');
    }

    try {
      await authApi.post('/register', data);
    } catch (error) {
      const axiosError = error as AxiosError<ApiErrorResponse>;
      throw new Error(
        axiosError.response?.data?.message || 
        'Registration failed. Please try again later.'
      );
    }
  }

  async logout(): Promise<void> {
    try {
      await authApi.post('/logout');
    } catch (error) {
      const axiosError = error as AxiosError;
      console.error('Logout error:', axiosError.message);
      // Continue with local cleanup even if server logout fails
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
    }
  }

  async getCurrentUser(): Promise<AuthState['user']> {
    try {
      const response = await authApi.get<AuthState['user']>('/me');
      return response.data;
    } catch (error) {
      const axiosError = error as AxiosError;
      console.error('Error fetching current user:', axiosError.message);
      return null;
    }
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  }
}

export const authService = new AuthService();
