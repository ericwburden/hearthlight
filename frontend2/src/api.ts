import axios from 'axios';
import { apiUrl } from '@/env';
import {
  INode,
  INodeCreate,
  INodeList,
  INodeWithChildren,
  IUserProfile,
  IUserProfileUpdate,
  IUserProfileCreate,
} from './interfaces';

function authHeaders(token: string) {
  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };
}

export const api = {
  // Authentication endpoints
  async logInGetToken(username: string, password: string) {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    return axios.post(`${apiUrl}/api/v1/login/access-token`, params);
  },
  async passwordRecovery(email: string) {
    return axios.post(`${apiUrl}/api/v1/password-recovery/${email}`);
  },
  async resetPassword(password: string, token: string) {
    return axios.post(`${apiUrl}/api/v1/reset-password/`, {
      NewPassword: password,
      token,
    });
  },

  // User endpoints
  async getMe(token: string) {
    return axios.get<IUserProfile>(`${apiUrl}/api/v1/users/me`, authHeaders(token));
  },
  async updateMe(token: string, data: IUserProfileUpdate) {
    return axios.put<IUserProfile>(`${apiUrl}/api/v1/users/me`, data, authHeaders(token));
  },
  async getUsers(token: string) {
    return axios.get<IUserProfile[]>(`${apiUrl}/api/v1/users/`, authHeaders(token));
  },
  async updateUser(token: string, userId: number, data: IUserProfileUpdate) {
    return axios.put(`${apiUrl}/api/v1/users/${userId}`, data, authHeaders(token));
  },
  async createUser(token: string, data: IUserProfileCreate) {
    return axios.post(`${apiUrl}/api/v1/users/`, data, authHeaders(token));
  },

  // Node endpoints
  async createNetwork(token: string, data: INodeCreate) {
    return axios.post<INode>(`${apiUrl}/api/v1/nodes/`, data, authHeaders(token));
  },
  async getNetworks(token: string) {
    return axios.get<INodeList>(`${apiUrl}/api/v1/nodes/networks/`, authHeaders(token));
  },
  async getNodeChildren(token: string, nodeId: number) {
    return axios.get<INodeWithChildren>(`${apiUrl}/api/v1/nodes/${nodeId}/children`, authHeaders(token));
  },
};
