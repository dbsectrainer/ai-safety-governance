import api from './api';

export interface ApiUser {
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

export interface CreateUserPayload {
  username: string;
  email: string;
  full_name?: string | null;
  password: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

export interface UpdateUserPayload {
  username?: string;
  email?: string;
  full_name?: string | null;
  password?: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

class UsersService {
  async listUsers(): Promise<ApiUser[]> {
    const response = await api.get<ApiUser[]>('/users/');
    return response.data;
  }

  async createUser(payload: CreateUserPayload): Promise<ApiUser> {
    const response = await api.post<ApiUser>('/users/', payload);
    return response.data;
  }

  async updateUser(id: number, payload: UpdateUserPayload): Promise<ApiUser> {
    const response = await api.put<ApiUser>(`/users/${id}`, payload);
    return response.data;
  }

  async deleteUser(id: number): Promise<void> {
    await api.delete(`/users/${id}`);
  }
}

export const usersService = new UsersService();
