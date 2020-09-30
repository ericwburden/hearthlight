import { INode, INodeList } from '@/interfaces';
import { AdminState } from './state';
import { getStoreAccessors } from 'typesafe-vuex';
import { State } from '../state';

export const mutations = {
  setNetworks(state: AdminState, payload: INodeList) {
    state.networks = payload;
  },
};

const { commit } = getStoreAccessors<AdminState | any, State>('');

export const commitSetNetworks = commit(mutations.setNetworks);
