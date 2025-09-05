import type { Project } from "@/types/project/Project";
import { filterByUserId } from "./filters.utils";

describe(filterByUserId.name, () => {
  it.each([
    [{ manager: { id: "1" } } as Project, "1"],
    [{ manager: { id: "1" }, supervisor: { id: "1" } } as Project, "1"],
    [
      {
        manager: {
          id: "1",
        },
        supervisor: {
          id: "1",
        },
        additionalSupervisors: [],
      } as unknown as Project,
      "1",
    ],
  ])(
    "should return true when the manager, supervisor and additional supervisors match the user id",
    (project, userId) => {
      expect(filterByUserId(project, userId)).toBe(true);
    }
  );

  it.each([
    [{} as Project, "1"],
    [
      {
        manager: {
          id: "1",
        },
        supervisor: {
          id: "1",
        },
        additionalSupervisors: [{ id: "1" }],
      } as Project,
      "2",
    ],
  ])(
    "should return true when the manager, supervisor and additional supervisors match the user id",
    (project, userId) => {
      expect(filterByUserId(project, userId)).toBeFalsy(); // it can return undefined or false
    }
  );
});
