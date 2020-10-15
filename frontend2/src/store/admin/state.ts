import {
  ApplicationModelEntry,
  INode,
  INodeList,
  IUserProfile,
  IUserGroup,
  IUserGroupList,
  IUserProfileList,
} from '@/interfaces';

export interface AdminState {
  applicationModel: ApplicationModelEntry[];
  activeNode: INode | null;
  networks: INodeList;
  nodes: INodeList;
  activeUser: IUserProfile | null;
  users: IUserProfileList;
  activeUserGroup: IUserGroup | null;
  userGroups: IUserGroupList;
}
