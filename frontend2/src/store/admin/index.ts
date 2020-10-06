/* eslint-disable @typescript-eslint/camelcase */

import { mutations } from './mutations';
import { getters } from './getters';
import { actions } from './actions';
import { AdminState } from './state';

const defaultState: AdminState = {
  applicationModel: [],
  networks: { total_records: 0, records: [] },
  nodeTypes: [],
  activeNode: null,
  nodes: { total_records: 0, records: [] },
  activeUserGroup: null,
  userGroups: { total_records: 0, records: [] },
  activeUser: null,
  users: { total_records: 0, records: [] },
};

export const adminModule = {
  state: defaultState,
  mutations,
  actions,
  getters,
};
