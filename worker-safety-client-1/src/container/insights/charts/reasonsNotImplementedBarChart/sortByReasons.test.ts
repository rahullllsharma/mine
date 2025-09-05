import { shuffle } from "lodash";
import { mockTenantStore } from "@/utils/dev/jest";
import { sortByReasons } from "./sortByReasons";

describe("sortByReasons", () => {
  mockTenantStore();
  const expectedOrder = [
    "Control was not available",
    "Control was not relevant",
    "Other controls in place",
    "Planned but not implemented",
  ];

  const data = [
    { reason: "Control was not relevant", count: 1 },
    { reason: "Other controls in place", count: 2 },
    { reason: "Planned but not implemented", count: 3 },
    { reason: "Control was not available", count: 4 },
    { reason: "Some unsupported reason", count: 5 },
  ];

  it("always sorts passed data as expected", () => {
    const sorted = sortByReasons(data);
    expect(sorted.map(x => x.reason)).toEqual(expectedOrder);

    // old timey for loop!
    for (let i = 0; i++; i < 5) {
      // shuffle data to be sure this works
      const shuffled = shuffle(data);
      const sortedByReasons = sortByReasons(shuffled);
      expect(sortedByReasons.map(x => x.reason)).toEqual(expectedOrder);
    }
  });

  it("ensures missing reasons are included", () => {
    const sorted = sortByReasons([]);
    expect(sorted.map(x => x.reason)).toEqual(expectedOrder);
    sorted.forEach(x => expect(x.count).toEqual(0));
  });
});
