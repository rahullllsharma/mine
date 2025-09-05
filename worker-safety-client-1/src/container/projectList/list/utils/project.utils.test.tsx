import { capitalize } from "lodash-es";
import { ProjectStatus } from "@/types/project/ProjectStatus";
import { mockTenantStore } from "@/utils/dev/jest";
import { getProjectStatusById, getProjectStatusLabel } from "./project.utils";

describe("Project Helper", () => {
  beforeAll(() => {
    mockTenantStore();
  });

  describe(getProjectStatusById.name, () => {
    it.each(Object.keys(ProjectStatus))(
      "should return the id and name for each status - $s",
      status => {
        expect(getProjectStatusById(status as ProjectStatus)).toMatchObject({
          id: status,
          name: capitalize(ProjectStatus[status as ProjectStatus]),
        });
      }
    );
  });

  describe(getProjectStatusLabel.name, () => {
    it.each(Object.keys(ProjectStatus))(
      "should return the name for each status - $s",
      status => {
        expect(getProjectStatusLabel(status as ProjectStatus)).toEqual(
          capitalize(ProjectStatus[status as ProjectStatus])
        );
      }
    );
  });
});
