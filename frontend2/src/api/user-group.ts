import axios from 'axios';
import { apiUrl } from '@/env';
import { authHeaders } from './headers';
import {
  IUserGroup,
  IUserGroupCreate,
  IUserGroupList,
  IUserGroupUpdate,
  IUserProfile,
  IUserProfileList,
} from '@/interfaces';

export const userGroup = {
  async createUserGroup(token: string, data: IUserGroupCreate) {
    return axios.post<IUserGroup>(`${apiUrl}/api/v1/user_groups/`, data, authHeaders(token));
  },
  async deleteUserGroup(token: string, userGroupID: number) {
    return axios.delete<IUserGroup>(`${apiUrl}/api/v1/user_groups/${userGroupID}`, authHeaders(token));
  },
  async getOneUserGroup(token: string, userGroupID: number) {
    return axios.get<IUserGroup>(`${apiUrl}/api/v1/user_groups/${userGroupID}`, authHeaders(token));
  },
  async updateUserGroup(token: string, userGroupID: number, data: IUserGroupUpdate) {
    return axios.put(`${apiUrl}/api/v1/user_groups/${userGroupID}`, data, authHeaders(token));
  },
  async getUserGroups(token: string, skip = 0, limit = 10, sortBy = '', sortDesc = false) {
    return axios.get<IUserGroupList>(
      `${apiUrl}/api/v1/user_groups/?skip=${skip}&limit=${limit}&sort_by=${sortBy}&sort_desc=${sortDesc}`,
      authHeaders(token),
    );
  },
  async addUserToGroup(token: string, userGroupID: number, userID: number) {
    return axios.get<{ user_group_id: number; user_id: number }>(
      `${apiUrl}/api/v1/user_groups/${userGroupID}/users/${userID}`,
      authHeaders(token),
    );
  },
  async removeUserFromGroup(token: string, userGroupID: number, userID: number) {
    return axios.delete<IUserProfile>(
      `${apiUrl}/api/v1/user_groups/${userGroupID}/users/${userID}`,
      authHeaders(token),
    );
  },
  async getUsersInGroup(token: string, userGroupID: number, skip = 0, limit = 10, sortBy = '', sortDesc = false) {
    return axios.get<IUserProfileList>(
      `${apiUrl}/api/v1/user_groups/${userGroupID}/users/
      ?skip=${skip}&limit=${limit}&sort_by=${sortBy}&sort_desc=${sortDesc}`,
      authHeaders(token),
    );
  },
  async getUsersNotInGroup(token: string, userGroupID: number, skip = 0, limit = 10, sortBy = '', sortDesc = false) {
    return axios.get<IUserProfileList>(
      `${apiUrl}/api/v1/user_groups/${userGroupID}/not/users/
      ?skip=${skip}&limit=${limit}&sort_by=${sortBy}&sort_desc=${sortDesc}`,
      authHeaders(token),
    );
  },
};
