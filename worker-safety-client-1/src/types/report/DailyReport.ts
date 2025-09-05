import type { CreatedBy } from "./../project/CreatedBy";
import type { User } from "./../User";
import type { DailyReportInputs } from "./DailyReportInputs";
import type { DailyReportStatus } from "./DailyReportStatus";

export type DailyReport = {
  id: string; // UUID
  createdBy: CreatedBy;
  createdAt: string; // Date;
  completedBy?: User;
  completedAt?: string; // Date;
  sectionsJSON?: Record<string, unknown>;
  sections?: DailyReportInputs;
  status: DailyReportStatus;
};

export type DailyReportUpdateData = {
  id: string; // UUID
  status: DailyReportStatus;
};

export type DailyReportFormHistory = {
  id: string; // UUID
  createdBy: CreatedBy;
  createdAt: string; // Date;
  completedBy?: User;
  completedAt?: string; // Date;
  sectionsJSON?: Record<string, unknown>;
  sections?: DailyReportInputs;
  status: DailyReportStatus;
  updatedAt: string; // Date;
  __typename: string;
};
