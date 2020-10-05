import axios from 'axios';
import { apiUrl } from '@/env';
import {
  INode,
  INodeChild,
  INodeCreate,
  INodeList,
  INodeUpdate,
  IUserGroup,
  IUserGroupCreate,
  IUserGroupList,
  IUserGroupUpdate,
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
  async createNode(token: string, data: INodeCreate) {
    return axios.post<INode>(`${apiUrl}/api/v1/nodes/`, data, authHeaders(token));
  },
  async deleteNode(token: string, nodeId: number) {
    return axios.delete<INode>(`${apiUrl}/api/v1/nodes/${nodeId}`, authHeaders(token));
  },
  async getOneNode(token: string, nodeId: number) {
    return axios.get<INode>(`${apiUrl}/api/v1/nodes/${nodeId}`, authHeaders(token));
  },
  async updateNode(token: string, nodeId: number, data: INodeUpdate) {
    return axios.put(`${apiUrl}/api/v1/nodes/${nodeId}`, data, authHeaders(token));
  },
  async getNetworks(token: string) {
    return axios.get<INodeList>(`${apiUrl}/api/v1/nodes/networks/`, authHeaders(token));
  },
  async getNodes(token: string, skip = 0, limit = 10, sort_by = '', sort_desc = false) {
    return axios.get<INodeList>(
      `${apiUrl}/api/v1/nodes/?skip=${skip}&limit=${limit}&sort_by=${sort_by}&sort_desc=${sort_desc}`,
      authHeaders(token),
    );
  },
  async getNodeChildren(token: string, nodeId: number) {
    return axios.get<INodeChild[]>(`${apiUrl}/api/v1/nodes/${nodeId}/children`, authHeaders(token));
  },
  async getNodeTypes() {
    return axios.get<string[]>(`${apiUrl}/api/v1/utils/node-types/`);
  },

  // User Group endpoints
  async createUserGroup(token: string, data: IUserGroupCreate) {
    return axios.post<IUserGroup>(`${apiUrl}/api/v1/user_groups/`, data, authHeaders(token));
  },
  async deleteUserGroup(token: string, UserGroupId: number) {
    return axios.delete<IUserGroup>(`${apiUrl}/api/v1/user_groups/${UserGroupId}`, authHeaders(token));
  },
  async getOneUserGroup(token: string, UserGroupId: number) {
    return axios.get<IUserGroup>(`${apiUrl}/api/v1/user_groups/${UserGroupId}`, authHeaders(token));
  },
  async updateUserGroup(token: string, UserGroupId: number, data: IUserGroupUpdate) {
    return axios.put(`${apiUrl}/api/v1/user_groups/${UserGroupId}`, data, authHeaders(token));
  },
  async getUserGroups(token: string, skip = 0, limit = 10, sort_by = '', sort_desc = false) {
    return axios.get<IUserGroupList>(
      `${apiUrl}/api/v1/user_groups/?skip=${skip}&limit=${limit}&sort_by=${sort_by}&sort_desc=${sort_desc}`,
      authHeaders(token),
    );
  },
};
