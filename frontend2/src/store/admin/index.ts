/* eslint-disable @typescript-eslint/camelcase */

import { mutations } from './mutations';
import { getters } from './getters';
import { actions } from './actions';
import { AdminState } from './state';

const defaultState: AdminState = {
  activeNode: null,
  applicationModel: [],
  configScreenShowForm: '',
  configureNodeFormProps: { id: null, title: '', parent: null, network: false, delete: false },
  networks: { total_records: 0, records: [] },
  nodes: { total_records: 0, records: [] },
  nodeTypes: [],
};

export const adminModule = {
  state: defaultState,
  mutations,
  actions,
  getters,
};
