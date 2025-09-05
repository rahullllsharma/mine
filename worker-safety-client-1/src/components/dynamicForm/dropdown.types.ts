export interface DataSourceColumnObject {
  attribute?: string;
  name?: string;
}

export type DataSourceColumn = DataSourceColumnObject | string;

export type RestDataSource = {
  id: string;
  name: string;
  columns?: DataSourceColumn[];
};
export enum ResponseOption {
  ManualEntry = "manual_entry",
  Fetch = "fetch",
}
