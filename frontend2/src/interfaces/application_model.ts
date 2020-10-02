export interface ApplicationModelEntry {
  id: number;
  name: string;
  type: string;
  children: ApplicationModelEntry[];
}

export interface IConfigureNodeFormProps {
  id: number | null;
  title: string;
  parent: number | null;
  network: boolean;
  delete: boolean;
}
