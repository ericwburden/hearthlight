/* eslint-disable @typescript-eslint/camelcase */
import axios from 'axios';
import { apiUrl } from '@/env';
import { authHeaders } from './headers';
import { InterfaceList } from '@/interfaces';

export const interfaces = {
  async getInterfaces(token: string, skip = 0, limit = 10, sortBy = '', sortDesc = false, name = '', interface_type = '') {
    return axios.get<InterfaceList>(
      `${apiUrl}/api/v1/interfaces/?skip=${skip}&limit=${limit}&sort_by=${sortBy}&sort_desc=${sortDesc}&name=${name}&node_type=${interface_type}`,
      authHeaders(token),
    );
  },
}
