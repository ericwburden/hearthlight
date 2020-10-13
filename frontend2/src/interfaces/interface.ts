export interface Interface {
  id: number;
  name: string;
  interface_type: string;
  created_at: Date;
  updated_at: Date;
  created_by_id: number;
  updated_by_id: number;
  [key: string]: number | string | Date;
}

export interface InterfaceList {
  total_records: number;
  records: Interface[];
}

export interface InterfaceCreate {
  name: string;
  interface_type: string;
}

export interface InterfaceUpdate {
  name?: string;
  interface_type?: string;
}