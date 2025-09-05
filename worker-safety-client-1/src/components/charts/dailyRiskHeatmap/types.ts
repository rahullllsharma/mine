/* eslint-disable @typescript-eslint/no-explicit-any */
import type { RiskLevel } from "@/components/riskBadge/RiskLevel";

export type RiskLevelByDate = {
  date: string;
  riskLevel: RiskLevel;
};

export type ProjectRiskLevelByDate = {
  projectName: string;
  riskLevelByDate: RiskLevelByDate[];
  dateToRiskLevel?: DateToRiskLevel;
};

export type LocationRiskLevelByDate = {
  locationName: string;
  riskLevelByDate: RiskLevelByDate[];
  dateToRiskLevel?: DateToRiskLevel;
};

export type TaskRiskLevelByDate = {
  taskName: string;
  locationName: string;
  projectName: string;
  riskLevelByDate: RiskLevelByDate[];
  dateToRiskLevel?: DateToRiskLevel;
};

export type EntityRiskLevelByDate =
  | ProjectRiskLevelByDate
  | LocationRiskLevelByDate
  | TaskRiskLevelByDate;

export type DateToRiskLevel = { [date: string]: RiskLevel };

export type ColumnDef = {
  id: string;
  Header: string;
  width?: number;
  value?: (row: any) => string;
  accessor?: (entityRisk: EntityRiskLevelByDate, index?: number) => any;
};
