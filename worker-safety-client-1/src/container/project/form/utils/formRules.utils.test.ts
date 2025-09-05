import { getRequiredFieldRules } from "./formRules.utils";

const RULES_OBJECT = {
  pattern: {
    message: "This field cannot be left blank",
    value: /.*[^ ].*/g,
  },
  required: "This is a required field",
};

describe(getRequiredFieldRules.name, () => {
  describe("if called with isRequired a true", () => {
    it("should return the rules object", () => {
      expect(getRequiredFieldRules(true)).toEqual(RULES_OBJECT);
    });
  });
  describe("if called with isRequired a false", () => {
    it("should return the an empty object", () => {
      expect(getRequiredFieldRules(false)).toEqual({});
    });
  });
});
