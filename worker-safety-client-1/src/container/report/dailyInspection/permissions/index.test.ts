import type { AuthUser } from "@/types/auth/AuthUser";
import {
  canDeleteOwnReport,
  canDeleteReports,
  canDownloadReports,
  canEditOwnReport,
  canEditReports,
  canReopenReports,
  canViewProject,
  canViewReports,
} from ".";

const user: AuthUser = {
  id: "a",
  initials: "",
  name: "",
  email: "",
  permissions: [],
  role: "supervisor",
  opco: null,
  userPreferences: [],
};

describe(canDeleteReports.name, () => {
  it("should return false when the user does not have permissions", () => {
    expect(canDeleteReports(user)).toBe(false);
  });

  it("should return true when the user does have permissions", () => {
    expect(canDeleteReports({ ...user, permissions: ["DELETE_REPORTS"] })).toBe(
      true
    );
  });
});

describe(canDeleteOwnReport.name, () => {
  it("should return false when the user does not have permissions", () => {
    expect(canDeleteOwnReport(user, "a")).toBe(false);
  });

  it("should return false when the user does have permissions but its not his report", () => {
    expect(
      canDeleteOwnReport({ ...user, permissions: ["DELETE_OWN_REPORTS"] }, "b")
    ).toBe(false);
  });

  it("should return true when the user does have permissions and its his report", () => {
    expect(
      canDeleteOwnReport({ ...user, permissions: ["DELETE_OWN_REPORTS"] }, "a")
    ).toBe(true);
  });
});

describe(canEditReports.name, () => {
  it("should return false when the user does not have permissions", () => {
    expect(canEditReports(user)).toBe(false);
  });

  it("should return true when the user does have permissions", () => {
    expect(canEditReports({ ...user, permissions: ["EDIT_REPORTS"] })).toBe(
      true
    );
  });
});

describe(canEditOwnReport.name, () => {
  it("should return false when the user does not have permissions", () => {
    expect(canEditOwnReport(user, "a")).toBe(false);
  });

  it("should return false when the user does have permissions but its not his report", () => {
    expect(
      canEditOwnReport({ ...user, permissions: ["EDIT_OWN_REPORTS"] }, "b")
    ).toBe(false);
  });

  it("should return true when the user does have permissions and its his report", () => {
    expect(
      canEditOwnReport({ ...user, permissions: ["EDIT_OWN_REPORTS"] }, "a")
    ).toBe(true);
  });
});

describe(canReopenReports.name, () => {
  it("should return false when the user does not have permissions", () => {
    expect(canReopenReports(user)).toBe(false);
  });

  it("should return true when the user does have permissions", () => {
    expect(canReopenReports({ ...user, permissions: ["REOPEN_REPORTS"] })).toBe(
      true
    );
  });

  describe(canDownloadReports.name, () => {
    it.each([
      {
        currentUser: {
          ...user,
          role: "viewer",
        },
        expected: true,
      },
      {
        currentUser: {
          ...user,
          role: "supervisor",
          id: "2",
        },
        expected: true,
      },
      {
        currentUser: {
          ...user,
          role: "supervisor",
          id: "1",
        },
        expected: true,
      },
      {
        currentUser: {
          ...user,
          role: "manager",
          id: "2",
        },
        expected: true,
      },
      {
        currentUser: {
          ...user,
          role: "administrator",
          id: "2",
        },
        expected: true,
      },
    ])(
      "should return $expected for the $currentUser",
      ({ currentUser, expected }) => {
        expect(canDownloadReports(currentUser as AuthUser)).toEqual(expected);
      }
    );
  });

  describe(canViewReports.name, () => {
    it("should return false when the user does not have permissions", () => {
      expect(canViewReports(user)).toBe(false);
    });

    it("should return true when the user does have permissions", () => {
      expect(
        canViewReports({ ...user, permissions: ["VIEW_INSPECTIONS"] })
      ).toBe(true);
    });
  });
});

describe(canViewProject.name, () => {
  it("should return false when the user does not have permissions", () => {
    expect(canViewProject(user)).toBe(false);
  });

  it("should return true when the user does have permissions", () => {
    expect(canViewProject({ ...user, permissions: ["VIEW_PROJECT"] })).toBe(
      true
    );
  });
});
