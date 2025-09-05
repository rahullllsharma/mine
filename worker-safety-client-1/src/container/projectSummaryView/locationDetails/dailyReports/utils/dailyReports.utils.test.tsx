import type { AuthUser } from "@/types/auth/AuthUser";
import type { DailyReport } from "@/types/report/DailyReport";
import { DailyReportStatus } from "@/types/report/DailyReportStatus";
import { getMenuIcon } from "./dailyReports.utils";

const user: AuthUser = {
  id: "a",
  initials: "",
  name: "",
  email: "super@email.local.urbinternal.com",
  permissions: [],
  role: "supervisor",
  opco: null,
  userPreferences: [],
};

const completedReport: DailyReport = {
  id: "6162b039-40ad-486f-b6f7-2efb3822c437",
  createdBy: {
    id: "bab6fc84-63c3-4fe5-b7a6-137e26189ad9",
    name: "Test User",
  },
  createdAt: "2022-02-02T09:32:20.464954",
  completedBy: {
    id: "bab6fc84-63c3-4fe5-b7a6-137e26189ad9",
    name: "Test User",
  },
  completedAt: "2022-02-02T09:32:20.464954",
  status: DailyReportStatus.COMPLETE,
};

const inProgressReport: DailyReport = {
  id: "6162b039-40ad-486f-b6f7-2efb3822c437",
  createdBy: {
    id: "bab6fc84-63c3-4fe5-b7a6-137e26189ad9",
    name: "Test User",
  },
  createdAt: "2022-02-02T09:32:20.464954",
  status: DailyReportStatus.IN_PROGRESS,
};

describe(getMenuIcon.name, () => {
  it('should return "edit" icon when the user has permissions to edit all reports or his own reports', () => {
    expect(
      getMenuIcon({ ...user, permissions: ["EDIT_REPORTS"] }, completedReport)
    ).toBe("edit");
  });

  it('should return "show" icon when the user has permissions view inspections and the report is completed', () => {
    expect(
      getMenuIcon(
        { ...user, permissions: ["VIEW_INSPECTIONS"] },
        completedReport
      )
    ).toBe("show");
  });

  it("should not return any icon when the user when the report is not completed", () => {
    expect(
      getMenuIcon(
        { ...user, permissions: ["VIEW_INSPECTIONS"] },
        inProgressReport
      )
    ).toBe(undefined);
  });
});
