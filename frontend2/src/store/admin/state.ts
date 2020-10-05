import {
  ApplicationModelEntry,
  IConfigureNodeFormProps,
  INode,
  INodeList,
  IUserGroup,
  IUserGroupList,
} from '@/interfaces';

export interface AdminState {
  applicationModel: ApplicationModelEntry[];
  activeNode: INode | null;
  activeUserGroup: IUserGroup | null;
  configScreenShowForm: string;
  configureNodeFormProps: IConfigureNodeFormProps;
  networks: INodeList;
  nodes: INodeList;
  nodeTypes: string[];
  userGroups: IUserGroupList;
}
