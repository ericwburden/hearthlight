import { authentication } from './authentication';
import { user } from './user';
import { userGroup } from './user-group';
import { node } from './node';
import { interfaces } from './interface';
import { utils } from './utils';

export const api = {
  // Authentication endpoints
  logInGetToken: authentication.logInGetToken,
  passwordRecovery: authentication.passwordRecovery,
  resetPassword: authentication.resetPassword,

  // User endpoints
  getMe: user.getMe,
  updateMe: user.updateMe,
  getUsers: user.getUsers,
  updateUser: user.updateUser,
  createUser: user.createUser,
  deleteUser: user.deleteUser,
  getOneUser: user.getOneUser,

  // Node endpoints
  createNode: node.createNode,
  deleteNode: node.deleteNode,
  getOneNode: node.getOneNode,
  updateNode: node.updateNode,
  getNetworks: node.getNetworks,
  getNodes: node.getNodes,
  getNodeChildren: node.getNodeChildren,

  // User Group endpoints
  createUserGroup: userGroup.createUserGroup,
  deleteUserGroup: userGroup.deleteUserGroup,
  getOneUserGroup: userGroup.getOneUserGroup,
  updateUserGroup: userGroup.updateUserGroup,
  getUserGroups: userGroup.getUserGroups,
  addUserToGroup: userGroup.addUserToGroup,
  removeUserFromGroup: userGroup.removeUserFromGroup,
  getUsersInGroup: userGroup.getUsersInGroup,
  getUsersNotInGroup: userGroup.getUsersNotInGroup,

  // Interface endpoints
  getInterfaces: interfaces.getInterfaces,

  // Utils endpoints
  getColumnNames: utils.getColumnNames,
  getNodeTypes: utils.getNodeTypes,
  getTableNames: utils.getTableNames,
};

export default api;
