export interface ApplicationModelEntry {
  id: number;
  name: string;
  type: string;
  key: string;
  children: ApplicationModelEntry[];
}

export interface IConfigureNodeFormProps {
  id: number | null;
  title: string;
  parent: number | null;
  network: boolean;
  delete: boolean;
}
