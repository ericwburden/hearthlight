export interface ApplicationModelEntry {
  id: number;
  name: string;
  type: string;
  key: string;
  children: ApplicationModelEntry[];
}
