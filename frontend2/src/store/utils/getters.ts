import { UtilsState } from './state';
import { getStoreAccessors } from 'typesafe-vuex';
import { State } from '../state';

export const getters = {
  columnNames: (state: UtilsState) => state.columnNames,
  tableNames: (state: UtilsState) => state.tableNames,
  nodeTypes: (state: UtilsState) => state.nodeTypes,
};

const { read } = getStoreAccessors<UtilsState, State>('');

export const readColumnNames = read(getters.columnNames);
export const readTableNames = read(getters.tableNames);
export const readNodeTypes = read(getters.nodeTypes);
