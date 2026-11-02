// Input validation patterns shared by the authentication forms. The backend
// enforces the same rules; client-side validation is only a UX helper.
export const validationPatterns = {
  email: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  password: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,128}$/,
  username: /^[a-zA-Z0-9_-]{3,16}$/,
  name: /^[a-zA-Z\s'-]{2,100}$/,
};

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  roles: string[];
  created_at: string;
  updated_at: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: AuthUser | null;
  token: string | null;
}

export const initialAuthState: AuthState = {
  isAuthenticated: false,
  user: null,
  token: null,
};

/** Whether the user should be treated as an administrator in the UI. */
export const isAdministrator = (user: AuthUser | null): boolean =>
  Boolean(user?.is_superuser || user?.roles?.includes('admin'));
