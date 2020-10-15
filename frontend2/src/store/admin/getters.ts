import { AdminState } from './state';
import { getStoreAccessors } from 'typesafe-vuex';
import { State } from '../state';

export const getters = {
  applicationModel: (state: AdminState) => state.applicationModel,
  networks: (state: AdminState) => state.networks,
  activeNode: (state: AdminState) => state.activeNode,
  nodes: (state: AdminState) => state.nodes,
  activeUserGroup: (state: AdminState) => state.activeUserGroup,
  userGroups: (state: AdminState) => state.userGroups,
  activeUser: (state: AdminState) => state.activeUser,
  users: (state: AdminState) => state.users,
};

const { read } = getStoreAccessors<AdminState, State>('');

export const readActiveNode = read(getters.activeNode);
export const readApplicationModel = read(getters.applicationModel);
export const readNetworks = read(getters.networks);
export const readAdminNodes = read(getters.nodes);

export const readActiveUserGroup = read(getters.activeUserGroup);
export const readUserGroups = read(getters.userGroups);

export const readActiveUser = read(getters.activeUser);
export const readUsers = read(getters.users);
