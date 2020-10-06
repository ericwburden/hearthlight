import { AdminState } from './state';
import { getStoreAccessors } from 'typesafe-vuex';
import { State } from '../state';

export const getters = {
  activeNode: (state: AdminState) => state.activeNode,
  activeUserGroup: (state: AdminState) => state.activeUserGroup,
  applicationModel: (state: AdminState) => state.applicationModel,
  networks: (state: AdminState) => state.networks,
  nodes: (state: AdminState) => state.nodes,
  nodeTypes: (state: AdminState) => state.nodeTypes,
  userGroups: (state: AdminState) => state.userGroups,
};

const { read } = getStoreAccessors<AdminState, State>('');

export const readActiveNode = read(getters.activeNode);
export const readApplicationModel = read(getters.applicationModel);
export const readNetworks = read(getters.networks);
export const readAdminNodes = read(getters.nodes);
export const readNodeTypes = read(getters.nodeTypes);

export const readActiveUserGroup = read(getters.activeUserGroup);
export const readUserGroups = read(getters.userGroups);
