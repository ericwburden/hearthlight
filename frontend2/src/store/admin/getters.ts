import { AdminState } from './state';
import { getStoreAccessors } from 'typesafe-vuex';
import { State } from '../state';

export const getters = {
  networks: (state: AdminState) => state.networks,
};

const { read } = getStoreAccessors<AdminState, State>('');

export const readNetworks = read(getters.networks);
