import { api } from '@/api';
import { getStoreAccessors } from 'typesafe-vuex';
import { ActionContext } from 'vuex';
import { State } from '../state';
import { commitSetColumnNames, commitSetNodeTypes, commitSetTableNames } from './mutations';
import { UtilsState } from './state';
import { MainState } from '../main/state';
import { dispatchCheckApiError } from '../main/actions';

type MainContext = ActionContext<MainState, State>;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const { dispatch } = getStoreAccessors<UtilsState | MainState | any, State>('');

export const actions = {
  async actionGetColumnNames(context: MainContext, payload: string) {
    try {
      const response = await api.getColumnNames(payload);
      if (response.data) {
        commitSetColumnNames(context, response.data);
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionGetNodeTypes(context: MainContext) {
    try {
      const response = await api.getNodeTypes();
      if (response.data) {
        commitSetNodeTypes(context, response.data);
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionGetTableNames(context: MainContext) {
    try {
      const response = await api.getTableNames();
      if (response.data) {
        commitSetTableNames(context, response.data);
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
};

export const dispatchGetColumnNames = dispatch(actions.actionGetColumnNames);
export const dispatchGetNodeTypes = dispatch(actions.actionGetNodeTypes);
export const dispatchGetTableNames = dispatch(actions.actionGetTableNames);
