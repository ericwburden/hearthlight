import { InterfaceList } from '@/interfaces';
import { InterfaceState } from './state';
import { getStoreAccessors } from 'typesafe-vuex';
import { State } from '../state';

export const mutations = {
  setInterfaces(state: InterfaceState, payload: InterfaceList) {
    state.interfaces = payload;
  },
};

// eslint-disable-next-line
const { commit } = getStoreAccessors<InterfaceState | any, State>('');

export const commitSetInterfaces = commit(mutations.setInterfaces);
