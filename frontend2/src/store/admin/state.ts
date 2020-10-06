import { ApplicationModelEntry, INode, INodeList, IUserGroup, IUserGroupList } from '@/interfaces';

export interface AdminState {
  applicationModel: ApplicationModelEntry[];
  activeNode: INode | null;
  networks: INodeList;
  nodes: INodeList;
  nodeTypes: string[];
  activeUserGroup: IUserGroup | null;
  userGroups: IUserGroupList;
}
