import axios from 'axios';
import { apiUrl } from '@/env';
import { IUserProfile, IUserProfileList, IUserProfileUpdate, IUserProfileCreate } from '@/interfaces';
import { authHeaders } from './headers';

export const user = {
  async getMe(token: string) {
    return axios.get<IUserProfile>(`${apiUrl}/api/v1/users/me`, authHeaders(token));
  },
  async updateMe(token: string, data: IUserProfileUpdate) {
    return axios.put<IUserProfile>(`${apiUrl}/api/v1/users/me`, data, authHeaders(token));
  },
  async getUsers(token: string, skip = 0, limit = 10, sortBy = '', sortDesc = false, fullName = '', email = '') {
    return axios.get<IUserProfileList>(
      `${apiUrl}/api/v1/users/?skip=${skip}&limit=${limit}&sort_by=${sortBy}&sort_desc=${sortDesc}&full_name=${fullName}&email=${email}`,
      authHeaders(token),
    );
  },
  async updateUser(token: string, userId: number, data: IUserProfileUpdate) {
    return axios.put(`${apiUrl}/api/v1/users/${userId}`, data, authHeaders(token));
  },
  async createUser(token: string, data: IUserProfileCreate) {
    return axios.post<IUserProfile>(`${apiUrl}/api/v1/users/`, data, authHeaders(token));
  },
  async deleteUser(token: string, userId: number) {
    return axios.delete<IUserProfile>(`${apiUrl}/api/v1/users/${userId}`, authHeaders(token));
  },
  async getOneUser(token: string, userId: number) {
    return axios.get<IUserProfile>(`${apiUrl}/api/v1/users/${userId}`, authHeaders(token));
  },
};
