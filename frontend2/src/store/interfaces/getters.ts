import { InterfaceState } from './state';
import { getStoreAccessors } from 'typesafe-vuex';
import { State } from '../state';

export const getters = {
  interfaces: (state: InterfaceState) => state.interfaces,
};

const { read } = getStoreAccessors<InterfaceState, State>('');

export const readInterfaces = read(getters.interfaces);
