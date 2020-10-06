import {
  ApplicationModelEntry,
  INode,
  INodeList,
  IUserGroup,
  IUserGroupList,
  IUserProfile,
  IUserProfileList,
} from '@/interfaces';
import { AdminState } from './state';
import { getStoreAccessors } from 'typesafe-vuex';
import { State } from '../state';

export const mutations = {
  initApplicationModel(state: AdminState, payload: INodeList) {
    const networkEntries: ApplicationModelEntry[] = payload.records.map((network: INode) => {
      return {
        id: network.id,
        type: 'network',
        name: network.name,
        key: `network-${network.id}`,
        children: [],
      };
    });
    state.applicationModel = networkEntries;
  },
  setApplicationModel(state: AdminState, payload: ApplicationModelEntry[]) {
    state.applicationModel = payload;
  },
  setNetworks(state: AdminState, payload: INodeList) {
    state.networks = payload;
  },
  setNodeTypes(state: AdminState, payload: string[]) {
    state.nodeTypes = payload;
  },
  setActiveNode(state: AdminState, payload: INode) {
    state.activeNode = payload;
  },
  setNodes(state: AdminState, payload: INodeList) {
    state.nodes = payload;
  },
  setActiveUserGroup(state: AdminState, payload: IUserGroup) {
    state.activeUserGroup = payload;
  },
  setUserGroups(state: AdminState, payload: IUserGroupList) {
    state.userGroups = payload;
  },
  setActiveUser(state: AdminState, payload: IUserProfile) {
    state.activeUser = payload;
  },
  setUsers(state: AdminState, payload: IUserProfileList) {
    state.users = payload;
  },
};

// eslint-disable-next-line
const { commit } = getStoreAccessors<AdminState | any, State>('');

export const commitInitApplicationModel = commit(mutations.initApplicationModel);
export const commitSetActiveNode = commit(mutations.setActiveNode);
export const commitSetApplicationModel = commit(mutations.setApplicationModel);
export const commitSetNetworks = commit(mutations.setNetworks);
export const commitSetNodes = commit(mutations.setNodes);
export const commitSetNodeTypes = commit(mutations.setNodeTypes);

export const commitSetActiveUserGroup = commit(mutations.setActiveUserGroup);
export const commitSetUserGroups = commit(mutations.setUserGroups);

export const commitSetActiveUser = commit(mutations.setActiveUser);
export const commitSetUsers = commit(mutations.setUsers);
