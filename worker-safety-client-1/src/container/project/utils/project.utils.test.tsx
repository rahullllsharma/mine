import {
  isAuditNavigationTab,
  isDetailsNavigationTab,
  isLocationsNavigationTab,
} from "./project.utils";

describe("Project Helper", () => {
  describe("isDetailsNavigationTab", () => {
    it("should return true if the index is set to 0", () => {
      const result = isDetailsNavigationTab(0);
      expect(result).toBeTruthy();
    });
  });

  describe("isLocationsNavigationTab", () => {
    it("should return true if the index is set to 1", () => {
      const result = isLocationsNavigationTab(1);
      expect(result).toBeTruthy();
    });
  });

  describe("isAuditNavigationTab", () => {
    it("should return true if the index is set to 2", () => {
      const result = isAuditNavigationTab(2);
      expect(result).toBeTruthy();
    });
  });
});
