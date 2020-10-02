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
  parent_id?: number;
}

export interface INodeUpdate {
  parent_id?: number;
  node_type?: string;
  name?: string;
  is_active?: boolean;
}

export interface INodeChild {
  node_id: number;
  child_type: string;
  child_id: number;
  child_name: string;
}
