import { ApplicationModelEntry, IConfigureNodeFormProps, INode, INodeList } from '@/interfaces';

export interface AdminState {
  applicationModel: ApplicationModelEntry[];
  activeNode: INode | null;
  configScreenShowForm: string;
  configureNodeFormProps: IConfigureNodeFormProps;
  networks: INodeList;
  nodes: INodeList;
  nodeTypes: string[];
}
