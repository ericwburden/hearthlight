import axios from 'axios';
import { apiUrl } from '@/env';

export const utils = {
  async getColumnNames(tableName: string) {
    return axios.get<string[]>(`${apiUrl}/api/v1/utils/column-names/${tableName}`);
  },
  async getNodeTypes() {
    return axios.get<string[]>(`${apiUrl}/api/v1/utils/node-types/`);
  },
  async getTableNames() {
    return axios.get<string[]>(`${apiUrl}/api/v1/utils/table-names/`);
  },
};
