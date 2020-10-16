export interface FormInputTableColumn {
  column_name: string;
  data_type: string;
  args?: string[];
  kwargs?: Record<string, string>;
}

export interface FormInputTable {
  table_name: string;
  columns: FormInputTableColumn[];
}

export interface FormInput {
  id: number;
  name: string;
  template: FormInputTable;
  interface_type: string;
  table_created: boolean;
  created_at: Date;
  updated_at: Date;
  created_by_id: number;
  updated_by_id: number;
  [key: string]: number | string | Date | boolean | FormInputTable;
}

export interface FormInputList {
  total_records: number;
  records: FormInput[];
}

export interface FormInputCreate {
  name: string;
  template: FormInputTable;
}

export interface FormInputUpdate {
  name?: string;
  template?: FormInputTable;
}
