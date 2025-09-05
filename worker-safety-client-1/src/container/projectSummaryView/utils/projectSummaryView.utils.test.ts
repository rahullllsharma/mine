import type { Location } from "@/types/project/Location";
import { ProjectViewTab } from "@/types/project/ProjectViewTabs";
import { mockTenantStore } from "@/utils/dev/jest";
import {
  getBreadcrumbDetails,
  getLocationById,
  getProjectSourceById,
  getProjectTabIndex,
  getProjectViewTab,
} from "./projectSummaryView.utils";

describe("Project Summary View Helper", () => {
  mockTenantStore();
  describe("getProjectViewTab", () => {
    it("should return the option that matches the id", () => {
      const tab = getProjectViewTab(ProjectViewTab.TASKS);
      expect(tab.id).toEqual(ProjectViewTab.TASKS);
    });
  });

  describe("getProjectTabIndex", () => {
    it("should return the index of the selected options", () => {
      const index = getProjectTabIndex(ProjectViewTab.TASKS);
      expect(index).toEqual(1);
    });

    it('should return "0" if no option is provided', () => {
      const index = getProjectTabIndex();
      expect(index).toEqual(0);
    });

    it('should return "0" if the option doesn\'t match', () => {
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      const index = getProjectTabIndex("random");
      expect(index).toEqual(0);
    });
  });

  describe("getProjectSourceById", () => {
    it("should return the option based on the provided id", () => {
      const option = getProjectSourceById(1);
      expect(option).toEqual(ProjectViewTab.TASKS);
    });
  });

  describe("getBreadcrumbDetails", () => {
    it('should return map data if source equals "map"', () => {
      const result = getBreadcrumbDetails("Project", "map");
      expect(result.title).toBe("Map");
      expect(result.link).toBe("/map");
    });

    it('should return project data if source is provided but is different from "map"', () => {
      const result = getBreadcrumbDetails("Project", "something");
      expect(result.title).toBe("Project");
      expect(result.link).toBe("/projects");
    });

    it("should return project data if no source is provided", () => {
      const result = getBreadcrumbDetails("Project");
      expect(result.title).toBe("Project");
      expect(result.link).toBe("/projects");
    });
  });

  describe("getLocationById", () => {
    const locations = [
      {
        id: "1",
        name: "location 1",
      },
      {
        id: "2",
        name: "location 2",
      },
      {
        id: "3",
        name: "location 3",
      },
    ];

    it('should return the location that matches the provided "id"', () => {
      const location = getLocationById(locations as Location[], "2");
      expect(location.id).toBe("2");
    });

    it('should return the first location if no "id" is provided', () => {
      const location = getLocationById(locations as Location[]);
      expect(location.id).toBe("1");
    });

    it('should return the first location if the provided "id" doesn\'t exist', () => {
      const location = getLocationById(locations as Location[], "0");
      expect(location.id).toBe("1");
    });
  });
});
