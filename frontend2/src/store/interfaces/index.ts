/* eslint-disable @typescript-eslint/camelcase */

import { mutations } from './mutations';
import { getters } from './getters';
import { actions } from './actions';
import { InterfaceState } from './state';

const defaultState: InterfaceState = {
  interfaces: { total_records: 0, records: [] },
};

export const interfaceModule = {
  state: defaultState,
  mutations,
  actions,
  getters,
};
