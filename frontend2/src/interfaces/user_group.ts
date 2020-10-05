export interface IUserGroup {
  id: number;
  node_id: number;
  name: string;
  created_at: Date;
  updated_at: Date;
  created_by_id: number;
  updated_by_id: number;
  [key: string]: number | string | Date;
}

export interface IUserGroupList {
  total_records: number;
  records: IUserGroup[];
}

export interface IUserGroupCreate {
  name: string;
  node_id: number;
}

export interface IUserGroupUpdate {
  name?: string;
  node_id?: number;
}
