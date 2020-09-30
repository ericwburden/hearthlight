export interface INode {
  id: number;
  parent_id?: number;
  node_type: string;
  name: string;
  is_active: boolean;
  depth: number;
  created_at: Date;
  updated_at: Date;
  created_by_id: number;
  updated_by_id: number;
}

export interface INodeList {
  total_records: number;
  nodes: INode[];
}

export interface INodeCreate {
  node_type: string;
  name: string;
}

export interface INodeUpdate {
  parent_id?: number;
  node_type?: string;
  name?: string;
  is_active?: boolean;
}

export interface INodeChild {
  child_id: number;
  child_name: string;
}

export interface INodeChildList {
  child_type: string;
  children: INodeChild[];
}

export interface INodeWithChildren {
  node_id: number;
  node_type: string;
  node_name: string;
  child_lists: INodeChildList[];
}
