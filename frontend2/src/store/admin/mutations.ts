import {
  ApplicationModelEntry,
  IConfigureNodeFormProps,
  INode,
  INodeList,
  IUserGroup,
  IUserGroupList,
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
  setActiveNode(state: AdminState, payload: INode) {
    state.activeNode = payload;
  },
  setActiveUserGroup(state: AdminState, payload: IUserGroup) {
    state.activeUserGroup = payload;
  },
  setApplicationModel(state: AdminState, payload: ApplicationModelEntry[]) {
    state.applicationModel = payload;
  },
  setConfigScreenShowForm(state: AdminState, payload: string) {
    state.configScreenShowForm = payload;
  },
  setConfigureNodeFormProps(state: AdminState, payload: IConfigureNodeFormProps) {
    state.configureNodeFormProps = payload;
  },
  setNetworks(state: AdminState, payload: INodeList) {
    state.networks = payload;
  },
  setNodes(state: AdminState, payload: INodeList) {
    state.nodes = payload;
  },
  setNodeTypes(state: AdminState, payload: string[]) {
    state.nodeTypes = payload;
  },
  setUserGroups(state: AdminState, payload: IUserGroupList) {
    state.userGroups = payload;
  },
};

// eslint-disable-next-line
const { commit } = getStoreAccessors<AdminState | any, State>('');

export const commitInitApplicationModel = commit(mutations.initApplicationModel);
export const commitSetActiveNode = commit(mutations.setActiveNode);
export const commitSetApplicationModel = commit(mutations.setApplicationModel);
export const commitSetConfigScreenShowForm = commit(mutations.setConfigScreenShowForm);
export const commitSetConfigureNodeFormProps = commit(mutations.setConfigureNodeFormProps);
export const commitSetNetworks = commit(mutations.setNetworks);
export const commitSetNodes = commit(mutations.setNodes);
export const commitSetNodeTypes = commit(mutations.setNodeTypes);

export const commitSetActiveUserGroup = commit(mutations.setActiveUserGroup);
export const commitSetUserGroups = commit(mutations.setUserGroups);
