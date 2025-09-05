import { mapHazardsDrillDownData } from "./mapHazardsDrillDownData";

describe("mapHazardsDrillDownData", () => {
  it("should handle missing values", () => {
    const apiResponse = {};
    const result = mapHazardsDrillDownData(apiResponse);

    expect(result.byProject).toEqual([]);
    expect(result.byLocation).toEqual([]);
    expect(result.bySiteCondition).toEqual([]);
    expect(result.byTask).toEqual([]);
    expect(result.byTaskType).toEqual([]);
  });

  it("should map passed values when they are present", () => {
    const apiResponse = {
      applicableHazardsByLocation: [
        { count: 50, location: { name: "some location" } },
      ],
    };
    const result = mapHazardsDrillDownData(apiResponse);

    expect(result.byProject).toEqual([]);
    expect(result.byLocation).toEqual([{ count: 50, name: "some location" }]);
    expect(result.bySiteCondition).toEqual([]);
    expect(result.byTask).toEqual([]);
    expect(result.byTaskType).toEqual([]);
  });

  it("maps all lists as expected", () => {
    const apiResponse = {
      applicableHazardsByProject: [
        { count: 50, project: { name: "some project" } },
      ],
      applicableHazardsByLocation: [
        { count: 50, location: { name: "some location" } },
      ],
      applicableHazardsBySiteCondition: [
        { count: 50, librarySiteCondition: { name: "some site condition" } },
      ],
      applicableHazardsByTask: [
        {
          count: 50,
          libraryTask: { name: "some task", category: "some taskType" },
        },
      ],
      applicableHazardsByTaskType: [
        {
          count: 50,
          libraryTask: { name: "some task", category: "some taskType" },
        },
      ],
    };
    const result = mapHazardsDrillDownData(apiResponse);

    expect(result.byProject).toEqual([{ count: 50, name: "some project" }]);
    expect(result.byLocation).toEqual([{ count: 50, name: "some location" }]);
    expect(result.bySiteCondition).toEqual([
      { count: 50, name: "some site condition" },
    ]);
    expect(result.byTask).toEqual([{ count: 50, name: "some task" }]);
    expect(result.byTaskType).toEqual([{ count: 50, name: "some taskType" }]);
  });
});
