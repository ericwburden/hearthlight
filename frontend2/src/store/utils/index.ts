/* eslint-disable @typescript-eslint/camelcase */

import { mutations } from './mutations';
import { getters } from './getters';
import { actions } from './actions';
import { UtilsState } from './state';

const defaultState: UtilsState = {
  columnNames: [],
  nodeTypes: [],
  tableNames: [],
};

export const utilsModule = {
  state: defaultState,
  mutations,
  actions,
  getters,
};
