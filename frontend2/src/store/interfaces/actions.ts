/* eslint-disable @typescript-eslint/camelcase */

import { api } from '@/api';
import { getStoreAccessors } from 'typesafe-vuex';
import { ActionContext } from 'vuex';
import { State } from '../state';
import { commitSetInterfaces } from './mutations';
import { InterfaceState } from './state';
import { MainState } from '../main/state';
import { dispatchCheckApiError } from '../main/actions';

type MainContext = ActionContext<MainState, State>;

//eslint-disable-next-line
const { dispatch } = getStoreAccessors<InterfaceState | MainState | any, State>('');

export const actions = {
  async actionGetInterfaces(
    context: MainContext,
    payload: { skip: number; limit: number; sortBy: string; sortDesc: boolean; name: string; interfaceType: string },
  ) {
    try {
      const response = await api.getInterfaces(
        context.getters.token,
        payload.skip,
        payload.limit,
        payload.sortBy,
        payload.sortDesc,
        payload.name,
        payload.interfaceType,
      );
      if (response.data) {
        commitSetInterfaces(context, response.data);
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
};

export const dispatchGetInterfaces = dispatch(actions.actionGetInterfaces);
