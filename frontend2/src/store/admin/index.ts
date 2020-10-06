/* eslint-disable @typescript-eslint/camelcase */

import { mutations } from './mutations';
import { getters } from './getters';
import { actions } from './actions';
import { AdminState } from './state';

const defaultState: AdminState = {
  activeNode: null,
  activeUserGroup: null,
  applicationModel: [],
  networks: { total_records: 0, records: [] },
  nodes: { total_records: 0, records: [] },
  nodeTypes: [],
  userGroups: { total_records: 0, records: [] },
};

export const adminModule = {
  state: defaultState,
  mutations,
  actions,
  getters,
};
