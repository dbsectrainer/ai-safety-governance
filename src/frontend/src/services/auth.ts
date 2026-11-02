import api, { getErrorMessage } from './api';
import type { AuthState, AuthUser } from '../config/security';
import { validationPatterns } from '../config/security';

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData extends LoginCredentials {
  username: string;
  full_name: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user?: AuthUser;
}

class AuthService {
  private userCache: { token: string; user: AuthUser | null } | null = null;
  private userRequest: Promise<AuthUser | null> | null = null;

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
      throw new Error(
        'Password must be at least 8 characters and include uppercase, lowercase, number and special character',
      );
    }

    try {
      const formData = new FormData();
      formData.append('username', credentials.email);
      formData.append('password', credentials.password);

      const response = await api.post<LoginResponse>('/auth/token', formData);
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);

      const user = response.data.user ?? (await this.getCurrentUser());
      if (!user) {
        throw new Error('Login succeeded but the user profile could not be loaded');
      }
      this.userCache = { token: access_token, user };

      return {
        isAuthenticated: true,
        user,
        token: access_token,
      };
    } catch (error) {
      localStorage.removeItem('token');
      throw new Error(getErrorMessage(error));
    }
  }

  async register(data: RegisterData): Promise<void> {
    if (!this.validateEmail(data.email)) {
      throw new Error('Invalid email format');
    }
    if (!this.validatePassword(data.password)) {
      throw new Error(
        'Password must be at least 8 characters and include uppercase, lowercase, number and special character',
      );
    }
    if (!validationPatterns.username.test(data.username)) {
      throw new Error('Username must be 3-16 characters using letters, numbers, _ or -');
    }
    if (data.full_name && !validationPatterns.name.test(data.full_name)) {
      throw new Error('Full name must be 2-100 characters');
    }

    try {
      await api.post('/auth/register', {
        username: data.username,
        email: data.email,
        password: data.password,
        full_name: data.full_name || null,
      });
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  }

  async logout(): Promise<void> {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      // Logout is client-side; an unavailable API must not trap the user.
      console.warn('Logout request failed:', getErrorMessage(error));
    } finally {
      localStorage.removeItem('token');
      this.userCache = null;
      this.userRequest = null;
    }
  }

  async getCurrentUser(): Promise<AuthUser | null> {
    const token = localStorage.getItem('token');
    if (!token) {
      this.userCache = null;
      return null;
    }
    if (this.userCache?.token === token) {
      return this.userCache.user;
    }
    if (!this.userRequest) {
      this.userRequest = (async () => {
        try {
          const response = await api.get<AuthUser>('/users/me');
          return response.data;
        } catch {
          return null;
        } finally {
          this.userRequest = null;
        }
      })();
    }
    const user = await this.userRequest;
    this.userCache = { token, user };
    return user;
  }

  isAuthenticated(): boolean {
    return Boolean(localStorage.getItem('token'));
  }

  async hasRole(role: string): Promise<boolean> {
    const user = await this.getCurrentUser();
    return Boolean(user?.is_superuser || user?.roles?.includes(role));
  }
}

export const authService = new AuthService();
