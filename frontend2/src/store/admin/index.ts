/* eslint-disable @typescript-eslint/camelcase */

import { mutations } from './mutations';
import { getters } from './getters';
import { actions } from './actions';
import { AdminState } from './state';

const defaultState: AdminState = {
  networks: { total_records: 0, nodes: [] },
};

export const adminModule = {
  state: defaultState,
  mutations,
  actions,
  getters,
};
