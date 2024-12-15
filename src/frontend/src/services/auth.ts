import axios, { AxiosError } from 'axios';
import { axiosSecurityConfig, AuthState, validationPatterns } from '../config/security';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
const API_V1 = `${API_URL}/api/v1`;

// Create axios instance with security configurations
const authApi = axios.create({
  baseURL: `${API_V1}`,
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

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData extends LoginCredentials {
  username: string;
  name: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    username: string;
    roles: string[];
  };
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
      const formData = new FormData();
      formData.append('username', credentials.email); // FastAPI OAuth2 expects 'username'
      formData.append('password', credentials.password);

      const response = await authApi.post<LoginResponse>('/auth/token', formData);
      const { access_token, user } = response.data;
      
      localStorage.setItem('token', access_token);

      return {
        isAuthenticated: true,
        user,
        token: access_token,
      };
    } catch (error) {
      if (error instanceof AxiosError) {
        throw new Error(
          error.response?.data?.detail || 
          'Login failed. Please check your credentials and try again.'
        );
      }
      throw error;
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
      await authApi.post('/auth/register', data);
    } catch (error) {
      if (error instanceof AxiosError) {
        throw new Error(
          error.response?.data?.detail || 
          'Registration failed. Please try again later.'
        );
      }
      throw error;
    }
  }

  async logout(): Promise<void> {
    try {
      await authApi.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('token');
    }
  }

  async getCurrentUser(): Promise<AuthState['user']> {
    try {
      const response = await authApi.get('/users/me');
      return response.data;
    } catch (error) {
      console.error('Error fetching current user:', error);
      return null;
    }
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  }
}

export const authService = new AuthService();
