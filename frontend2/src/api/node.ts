import axios from 'axios';
import { apiUrl } from '@/env';
import { authHeaders } from './headers';
import { INode, INodeChild, INodeCreate, INodeList, INodeUpdate } from '@/interfaces';

export const node = {
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
  async getNodes(token: string, skip = 0, limit = 10, sortBy = '', sortDesc = false) {
    return axios.get<INodeList>(
      `${apiUrl}/api/v1/nodes/?skip=${skip}&limit=${limit}&sort_by=${sortBy}&sort_desc=${sortDesc}`,
      authHeaders(token),
    );
  },
  async getNodeChildren(token: string, nodeId: number) {
    return axios.get<INodeChild[]>(`${apiUrl}/api/v1/nodes/${nodeId}/children`, authHeaders(token));
  },
  async getNodeTypes() {
    return axios.get<string[]>(`${apiUrl}/api/v1/utils/node-types/`);
  },
};
