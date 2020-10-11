import { api } from '@/api';
import {
  ApplicationModelEntry,
  INodeCreate,
  INodeUpdate,
  IUserGroupCreate,
  IUserGroupUpdate,
  IUserProfileCreate,
  IUserProfileUpdate,
} from '@/interfaces';
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
  commitSetNodes,
  commitSetNodeTypes,
  commitSetActiveUserGroup,
  commitSetUserGroups,
  commitSetActiveUser,
  commitSetUsers,
} from './mutations';
import { AdminState } from './state';
import { MainState } from '../main/state';
import { dispatchCheckApiError } from '../main/actions';
import { commitAddNotification, commitRemoveNotification } from '../main/mutations';
import { readApplicationModel } from '../admin/getters';

type MainContext = ActionContext<MainState, State>;

//eslint-disable-next-line
const { dispatch } = getStoreAccessors<AdminState | MainState | any, State>('');

/* eslint-disable @typescript-eslint/camelcase */
export const actions = {
  // Node Actions
  async actionDeleteNode(context: MainContext, payload: number) {
    try {
      const loadingNotification = { content: `Deleting node: ID ${payload}`, showProgress: true };
      await api.deleteNode(context.getters.token, payload);
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
      (
        await Promise.all([
          api.createNode(context.getters.token, payload),
          await new Promise((resolve) => setTimeout(() => resolve(), 500)),
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
  async actionUpdateNode(context: MainContext, payload: { id: number; object: INodeUpdate }) {
    try {
      const loadingNotification = { content: `Updating node: ID ${payload.id}`, showProgress: true };
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.updateNode(context.getters.token, payload.id, payload.object),
          await new Promise((resolve) => setTimeout(() => resolve(), 500)),
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
  async actionGetNodes(
    context: MainContext,
    payload: { skip: number; limit: number; sortBy: string; sortDesc: boolean },
  ) {
    try {
      const response = await api.getNodes(
        context.getters.token,
        payload.skip,
        payload.limit,
        payload.sortBy,
        payload.sortDesc,
      );
      if (response.data) {
        commitSetNodes(context, response.data);
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
          const sorted_result = response.data.sort((a, b) => {
            if (a.child_type == b.child_type) return a.child_id - b.child_id;
            if (a.child_type < b.child_type) return 1;
            if (b.child_type > a.child_type) return -1;
            return 0;
          });
          const children = sorted_result.map((child) => {
            const childEntry: ApplicationModelEntry = {
              id: child.child_id,
              name: child.child_name,
              type: child.child_type,
              key: `${child.child_type}-${child.child_id}`,
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

  // UserGroup Actions
  async actionGetUserGroups(
    context: MainContext,
    payload: { skip: number; limit: number; sortBy: string; sortDesc: boolean },
  ) {
    try {
      const response = await api.getUserGroups(
        context.getters.token,
        payload.skip,
        payload.limit,
        payload.sortBy,
        payload.sortDesc,
      );
      if (response.data) {
        commitSetUserGroups(context, response.data);
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionGetOneUserGroup(context: MainContext, payload: number) {
    try {
      const response = await api.getOneUserGroup(context.getters.token, payload);
      if (response.data) {
        commitSetActiveUserGroup(context, response.data);
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionCreateUserGroup(context: MainContext, payload: IUserGroupCreate) {
    try {
      const loadingNotification = { content: `Saving new user group: ${payload.name}`, showProgress: true };
      commitAddNotification(context, loadingNotification);
      (
        await Promise.all([
          api.createUserGroup(context.getters.token, payload),
          await new Promise((resolve) => setTimeout(() => resolve(), 500)),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: `Created new user group: ${payload.name}`,
        color: 'success',
      });
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionUpdateUserGroup(context: MainContext, payload: { id: number; object: IUserGroupUpdate }) {
    try {
      const loadingNotification = { content: `Updating user group: ID ${payload.id}`, showProgress: true };
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.updateUserGroup(context.getters.token, payload.id, payload.object),
          await new Promise((resolve) => setTimeout(() => resolve(), 500)),
        ])
      )[0];
      commitSetActiveUserGroup(context, response.data);
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'User group successfully updated',
        color: 'success',
      });
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionDeleteUserGroup(context: MainContext, payload: number) {
    try {
      const loadingNotification = { content: `Deleting user group: ID ${payload}`, showProgress: true };
      await api.deleteUserGroup(context.getters.token, payload);
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: `User group ${payload} successfully deleted.`,
        color: 'success',
      });
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionAddUserToGroup(context: MainContext, payload: { userGroupID: number; userID: number }) {
    const userGroupID = payload.userGroupID;
    const userID = payload.userID;
    try {
      const loadingNotification = {
        content: `Adding user ${userID} to user group ${userGroupID}.`,
        showProgress: true,
      };
      await api.addUserToGroup(context.getters.token, userGroupID, userID);
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: `Successfully added user ${userID} to user group ${userGroupID}.`,
        color: 'success',
      });
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionRemoveUserFromGroup(context: MainContext, payload: { userGroupID: number; userID: number }) {
    const userGroupID = payload.userGroupID;
    const userID = payload.userID;
    try {
      const loadingNotification = {
        content: `Removing user ${userID} from user group ${userGroupID}.`,
        showProgress: true,
      };
      await api.removeUserFromGroup(context.getters.token, userGroupID, userID);
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: `Successfully removed user ${userID} from user group ${userGroupID}.`,
        color: 'success',
      });
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },

  // User Actions
  async actionCreateUser(context: MainContext, payload: IUserProfileCreate) {
    try {
      const loadingNotification = { content: `Saving new user: ${payload.email}`, showProgress: true };
      commitAddNotification(context, loadingNotification);
      (
        await Promise.all([
          api.createUser(context.getters.token, payload),
          await new Promise((resolve) => setTimeout(() => resolve(), 500)),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: `Created new user: ${payload.email}`,
        color: 'success',
      });
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionGetOneUser(context: MainContext, payload: number) {
    try {
      const response = await api.getOneUser(context.getters.token, payload);
      if (response.data) {
        commitSetActiveUser(context, response.data);
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionGetUsers(
    context: MainContext,
    payload: { skip: number; limit: number; sortBy: string; sortDesc: boolean; fullName: string; email: string },
  ) {
    try {
      const response = await api.getUsers(
        context.getters.token,
        payload.skip,
        payload.limit,
        payload.sortBy,
        payload.sortDesc,
        payload.fullName,
        payload.email,
      );
      if (response.data) {
        commitSetUsers(context, response.data);
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionGetUsersInGroup(
    context: MainContext,
    payload: { userGroupID: number; skip: number; limit: number; sortBy: string; sortDesc: boolean },
  ) {
    try {
      const response = await api.getUsersInGroup(
        context.getters.token,
        payload.userGroupID,
        payload.skip,
        payload.limit,
        payload.sortBy,
        payload.sortDesc,
      );
      if (response.data) {
        commitSetUsers(context, response.data);
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionGetUsersNotInGroup(
    context: MainContext,
    payload: { userGroupID: number; skip: number; limit: number; sortBy: string; sortDesc: boolean },
  ) {
    try {
      const response = await api.getUsersNotInGroup(
        context.getters.token,
        payload.userGroupID,
        payload.skip,
        payload.limit,
        payload.sortBy,
        payload.sortDesc,
      );
      if (response.data) {
        commitSetUsers(context, response.data);
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionUpdateUser(context: MainContext, payload: { id: number; object: IUserProfileUpdate }) {
    try {
      const loadingNotification = { content: `Updating user: ID ${payload.id}`, showProgress: true };
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.updateUser(context.getters.token, payload.id, payload.object),
          await new Promise((resolve) => setTimeout(() => resolve(), 500)),
        ])
      )[0];
      commitSetActiveUser(context, response.data);
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'User successfully updated',
        color: 'success',
      });
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionDeleteUser(context: MainContext, payload: number) {
    try {
      const loadingNotification = { content: `Deleting user: ID ${payload}`, showProgress: true };
      await api.deleteUser(context.getters.token, payload);
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: `User ${payload} successfully deleted.`,
        color: 'success',
      });
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
export const dispatchGetNodes = dispatch(actions.actionGetNodes);
export const dispatchGetNodeTypes = dispatch(actions.actionGetNodeTypes);
export const dispatchUpdateApplicationModelChildren = dispatch(actions.actionUpdateApplicationModelChildren);

export const dispatchGetUserGroups = dispatch(actions.actionGetUserGroups);
export const dispatchGetOneUserGroup = dispatch(actions.actionGetOneUserGroup);
export const dispatchCreateUserGroup = dispatch(actions.actionCreateUserGroup);
export const dispatchUpdateUserGroup = dispatch(actions.actionUpdateUserGroup);
export const dispatchDeleteUserGroup = dispatch(actions.actionDeleteUserGroup);
export const dispatchAddUserToGroup = dispatch(actions.actionAddUserToGroup);
export const dispatchRemoveUserFromGroup = dispatch(actions.actionRemoveUserFromGroup);

export const dispatchCreateUser = dispatch(actions.actionCreateUser);
export const dispatchGetOneUser = dispatch(actions.actionGetOneUser);
export const dispatchGetUsers = dispatch(actions.actionGetUsers);
export const dispatchGetUsersInGroup = dispatch(actions.actionGetUsersInGroup);
export const dispatchGetUsersNotInGroup = dispatch(actions.actionGetUsersNotInGroup);
export const dispatchUpdateUser = dispatch(actions.actionUpdateUser);
export const dispatchDeleteUser = dispatch(actions.actionDeleteUser);
