import { AdminState } from './state';
import { getStoreAccessors } from 'typesafe-vuex';
import { State } from '../state';

export const getters = {
  activeNode: (state: AdminState) => state.activeNode,
  applicationModel: (state: AdminState) => state.applicationModel,
  configScreenShowForm: (state: AdminState) => state.configScreenShowForm,
  configureNodeFormProps: (state: AdminState) => state.configureNodeFormProps,
  networks: (state: AdminState) => state.networks,
  nodeTypes: (state: AdminState) => state.nodeTypes,
};

const { read } = getStoreAccessors<AdminState, State>('');

export const readActiveNode = read(getters.activeNode);
export const readApplicationModel = read(getters.applicationModel);
export const readConfigScreenShowForm = read(getters.configScreenShowForm);
export const readConfigureNodeFormProps = read(getters.configureNodeFormProps);
export const readNetworks = read(getters.networks);
export const readNodeTypes = read(getters.nodeTypes);
