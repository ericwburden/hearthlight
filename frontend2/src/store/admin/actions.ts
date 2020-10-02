import { api } from '@/api';
import { INodeUpdate } from '@/interfaces';
import { searchApplicationModel } from '@/utils';
import { getStoreAccessors } from 'typesafe-vuex';
import { ActionContext } from 'vuex';
import { State } from '../state';
import { store } from '@/store';
import {
  commitInitApplicationModel,
  commitSetActiveNode,
  commitSetApplicationModel,
  commitSetNetworks,
  commitSetNodeTypes,
} from './mutations';
import { AdminState } from './state';
import { MainState } from '../main/state';
import { dispatchCheckApiError } from '../main/actions';
import { ApplicationModelEntry, INodeCreate } from '@/interfaces';
import { commitAddNotification, commitRemoveNotification } from '../main/mutations';
import { readApplicationModel } from '../admin/getters';

type MainContext = ActionContext<MainState, State>;

//eslint-disable-next-line
const { dispatch } = getStoreAccessors<AdminState | MainState | any, State>('');

export const actions = {
  async actionDeleteNode(context: MainContext, payload: number) {
    try {
      const loadingNotification = { content: `Deleting node: ID ${payload}`, showProgress: true };
      const response = await api.deleteNode(context.getters.token, payload);
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: `Node ${payload} successfully deleted.`,
        color: 'success',
      });
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionCreateNode(context: MainContext, payload: INodeCreate) {
    try {
      const node_type = payload.node_type == 'network' ? 'network' : 'node';
      const loadingNotification = { content: `Saving new ${node_type}: ${payload.name}`, showProgress: true };
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.createNode(context.getters.token, payload),
          await new Promise((resolve, reject) => setTimeout(() => resolve(), 500)),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: `Created new ${node_type}: ${payload.name}`,
        color: 'success',
      });
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionReadOneNode(context: MainContext, payload: number) {
    try {
      const response = await api.getOneNode(context.getters.token, payload);
      if (response.data) {
        commitSetActiveNode(context, response.data);
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionUpdateNode(context: MainContext, payload: [number, INodeUpdate]) {
    const nodeId = payload[0];
    const nodeUpdateObj = payload[1];
    try {
      const loadingNotification = { content: `Updating node: ID ${nodeId}`, showProgress: true };
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.updateNode(context.getters.token, nodeId, nodeUpdateObj),
          await new Promise((resolve, reject) => setTimeout(() => resolve(), 500)),
        ])
      )[0];
      commitSetActiveNode(context, response.data);
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Node successfully updated',
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

        // Check the networks already in the application Model
        commitInitApplicationModel(context, response.data);
        const networks = readApplicationModel(store);
        let network;
        for (network of networks) {
          await actions.actionUpdateApplicationModelChildren(context, network);
        }
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
  async actionUpdateApplicationModelChildren(context: MainContext, payload: ApplicationModelEntry) {
    try {
      if (payload.id) {
        const response = await api.getNodeChildren(context.getters.token, payload.id);
        const applicationModel = readApplicationModel(store);
        const applicationModelEntry = searchApplicationModel(applicationModel, payload.id, payload.type);
        if (applicationModelEntry) {
          const children = response.data.map((child) => {
            const childEntry: ApplicationModelEntry = {
              id: child.child_id,
              name: child.child_name,
              type: child.child_type,
              children: [],
            };
            return childEntry;
          });
          applicationModelEntry.children = children;
        }
        commitSetApplicationModel(store, applicationModel);
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
};

export const dispatchCreateNode = dispatch(actions.actionCreateNode);
export const dispatchDeleteNode = dispatch(actions.actionDeleteNode);
export const dispatchGetOneNode = dispatch(actions.actionReadOneNode);
export const dispatchUpdateNode = dispatch(actions.actionUpdateNode);
export const dispatchGetNetworks = dispatch(actions.actionGetNetworks);
export const dispatchGetNodeTypes = dispatch(actions.actionGetNodeTypes);
export const dispatchUpdateApplicationModelChildren = dispatch(actions.actionUpdateApplicationModelChildren);
