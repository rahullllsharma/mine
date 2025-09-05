import { parseOptions } from "./tab.utils";

const options = ["Active", "Pending"];
const expectedOptions = [
  { id: "0", name: "Active" },
  { id: "1", name: "Pending" },
];

describe("Tabs helper", () => {
  describe('when "parseOptions" is called', () => {
    it("should format the options", () => {
      expect(parseOptions(options)).toStrictEqual(expectedOptions);
    });
  });
});
