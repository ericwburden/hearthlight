import { api } from '@/api';
import { getStoreAccessors } from 'typesafe-vuex';
import { ActionContext } from 'vuex';
import { State } from '../state';
import { commitSetNetworks } from './mutations';
import { AdminState } from './state';
import { MainState } from '../main/state';
import { dispatchCheckApiError } from '../main/actions';
import { INodeCreate } from '@/interfaces';
import { commitAddNotification, commitRemoveNotification } from '../main/mutations';

type MainContext = ActionContext<MainState, State>;

const { dispatch } = getStoreAccessors<AdminState | MainState | any, State>('');

export const actions = {
  async actionCreateNetwork(context: MainContext, payload: INodeCreate) {
    try {
      const loadingNotification = { content: `Saving new network: ${payload.name}`, showProgress: true };
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.createNetwork(context.getters.token, payload),
          await new Promise((resolve, reject) => setTimeout(() => resolve(), 500)),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: `Created new network: ${payload.name}`,
        color: 'success',
      });
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionGetNetworks(context: MainContext) {
    try {
      const response = await api.getNetworks(context.getters.token);
      if (response.data) {
        commitSetNetworks(context, response.data);
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
};

export const dispatchGetNetworks = dispatch(actions.actionGetNetworks);
export const dispatchCreateNetwork = dispatch(actions.actionCreateNetwork);
