import type { MultiStepFormStateItem } from "../state/reducer";
import { formatSteps } from "./formatSteps.utils";

describe(formatSteps.name, () => {
  describe("when steps have one or more selected items", () => {
    it("should return the same array", () => {
      const expected = [
        { name: "tasks", isSelected: false, status: "default" },
      ] as MultiStepFormStateItem[];
      expect(formatSteps(expected)).toBe(expected);
    });
  });

  describe("when steps do not have selected items", () => {
    const result = formatSteps([
      { id: "tasks", name: "tasks" },
      { id: "work-schedule", name: "work-schedule" },
    ] as MultiStepFormStateItem[]);

    it("should define the 'isSelected' prop for each item", () => {
      expect(result.every(step => typeof step.isSelected === "boolean")).toBe(
        true
      );
    });

    it("should define the 'status' prop to 'default' for each item", () => {
      expect(result.every(step => step.status === "default")).toBe(true);
    });

    it("should define the 1st element as selected", () => {
      const [first, last] = result;
      expect(first.isSelected).toBe(true);
      expect(last.isSelected).toBe(false);
    });
  });
});
