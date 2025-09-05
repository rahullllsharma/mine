import { buildHazardOptions } from "./buildHazardOptions.utils";

describe(buildHazardOptions.name, () => {
  it("should return undefined when no argument is passed", () => {
    expect(buildHazardOptions()).toBeUndefined();
  });
  it("should return an object with a prefix and index when the argument passed follows the pattern `string.number`", () => {
    expect(buildHazardOptions("hello.0")).toMatchObject({
      prefix: "hello",
      taskIndex: 0,
    });
  });
});
