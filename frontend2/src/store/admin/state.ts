import { ApplicationModelEntry, INode, INodeList, IUserGroup, IUserGroupList } from '@/interfaces';

export interface AdminState {
  applicationModel: ApplicationModelEntry[];
  activeNode: INode | null;
  activeUserGroup: IUserGroup | null;
  networks: INodeList;
  nodes: INodeList;
  nodeTypes: string[];
  userGroups: IUserGroupList;
}
