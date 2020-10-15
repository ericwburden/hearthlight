import { UtilsState } from './state';
import { getStoreAccessors } from 'typesafe-vuex';
import { State } from '../state';

export const mutations = {
  setColumnNames(state: UtilsState, payload: string[]) {
    state.columnNames = payload;
  },
  setTableNames(state: UtilsState, payload: string[]) {
    state.tableNames = payload;
  },
  setNodeTypes(state: UtilsState, payload: string[]) {
    state.nodeTypes = payload;
  },
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const { commit } = getStoreAccessors<UtilsState | any, State>('');

export const commitSetColumnNames = commit(mutations.setColumnNames);
export const commitSetTableNames = commit(mutations.setTableNames);
export const commitSetNodeTypes = commit(mutations.setNodeTypes);
