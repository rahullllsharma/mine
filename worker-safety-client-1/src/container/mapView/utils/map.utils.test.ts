import type { LocationFilter } from "../filters/mapFilters/MapFilters";
import { parseFilters } from "./map.utils";

const filters: LocationFilter[] = [
  {
    field: "RISK",
    values: [
      { id: "1", name: "High" },
      { id: "2", name: "Medium" },
    ],
  },
  { field: "REGIONS", values: [] },
  { field: "DIVISIONS", values: [] },
];

describe("map.utils", () => {
  describe("parseFilters", () => {
    it("should remove the filters without values", () => {
      const result = parseFilters(filters);
      expect(result.map(filter => filter.field).join(",")).toBe("RISK");
    });
  });
});
