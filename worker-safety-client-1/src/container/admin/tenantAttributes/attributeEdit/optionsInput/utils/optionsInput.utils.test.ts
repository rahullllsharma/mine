import {
  isMandatoryField,
  shouldUpdateNonVisibleFields,
} from "./optionsInput.utils";

describe("OptionsInput/helpers", () => {
  describe(isMandatoryField.name, () => {
    describe("when mandatory is set to true", () => {
      it("should return true when value is a VALID_KEYS entry ", () => {
        expect(isMandatoryField(true, "visible")).toBe(true);
      });
      it("should return false when value is not a VALID_KEYS entry ", () => {
        expect(isMandatoryField(true, "filterable")).toBe(false);
      });
    });

    describe("when mandatory is set to false", () => {
      it("should return false even when value is a VALID_KEYS entry ", () => {
        expect(isMandatoryField(false, "visible")).toBe(false);
      });
      it("should return false when value is not a VALID_KEYS entry ", () => {
        expect(isMandatoryField(false, "filterable")).toBe(false);
      });
    });
  });

  describe(shouldUpdateNonVisibleFields.name, () => {
    it("should return true when key is 'visible'", () => {
      expect(shouldUpdateNonVisibleFields("visible")).toBe(true);
    });

    it("should return false when key is not 'visible'", () => {
      expect(shouldUpdateNonVisibleFields("required")).toBe(false);
    });
  });
});
