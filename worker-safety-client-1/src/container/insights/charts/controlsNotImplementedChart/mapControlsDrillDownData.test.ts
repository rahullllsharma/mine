import { mapControlsDrillDownData } from "./mapControlsDrillDownData";

describe("mapControlsDrillDownData", () => {
  it("should handle missing values", () => {
    const apiResponse = {};
    const result = mapControlsDrillDownData(apiResponse);

    expect(result.byProject).toEqual([]);
    expect(result.byLocation).toEqual([]);
    expect(result.byHazard).toEqual([]);
    expect(result.byTask).toEqual([]);
    expect(result.byTaskType).toEqual([]);
  });

  it("should map passed values when they are present", () => {
    const apiResponse = {
      notImplementedControlsByLocation: [
        { percent: 0.5, location: { name: "some location" } },
      ],
    };
    const result = mapControlsDrillDownData(apiResponse);

    expect(result.byProject).toEqual([]);
    expect(result.byLocation).toEqual([{ percent: 50, name: "some location" }]);
    expect(result.byHazard).toEqual([]);
    expect(result.byTask).toEqual([]);
    expect(result.byTaskType).toEqual([]);
  });

  it("maps all lists as expected", () => {
    const apiResponse = {
      notImplementedControlsByProject: [
        { percent: 0.5, project: { name: "some project" } },
      ],
      notImplementedControlsByLocation: [
        { percent: 0.5, location: { name: "some location" } },
      ],
      notImplementedControlsByHazard: [
        { percent: 0.5, libraryHazard: { name: "some hazard" } },
      ],
      notImplementedControlsByTask: [
        {
          percent: 0.5,
          libraryTask: { name: "some task", category: "some taskType" },
        },
      ],
      notImplementedControlsByTaskType: [
        {
          percent: 0.5,
          libraryTask: { name: "some task", category: "some taskType" },
        },
      ],
    };
    const result = mapControlsDrillDownData(apiResponse);

    expect(result.byProject).toEqual([{ percent: 50, name: "some project" }]);
    expect(result.byLocation).toEqual([{ percent: 50, name: "some location" }]);
    expect(result.byHazard).toEqual([{ percent: 50, name: "some hazard" }]);
    expect(result.byTask).toEqual([{ percent: 50, name: "some task" }]);
    expect(result.byTaskType).toEqual([{ percent: 50, name: "some taskType" }]);
  });
});
