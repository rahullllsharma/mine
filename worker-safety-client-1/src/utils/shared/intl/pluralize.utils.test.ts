import { pluralize } from "./pluralize.utils";

describe(pluralize.name, () => {
  beforeAll(() => {
    const PluralRulesImpl = Intl.PluralRules;
    jest.spyOn(Intl, "PluralRules").mockImplementation(() => {
      return new PluralRulesImpl("en-us");
    });
  });

  it("should return the plural form when passing the subject as 0", () => {
    expect(
      pluralize({ subject: 0, singular: "singular", plural: "plural" })
    ).toEqual("plural");
  });

  it("should return the plural form when passing the subject is an empty array", () => {
    expect(
      pluralize({ subject: [], singular: "singular", plural: "plural" })
    ).toEqual("plural");
  });

  describe("when passing a number", () => {
    it("should return the singular form when passing the subject as 1", () => {
      expect(
        pluralize({ subject: 1, singular: "singular", plural: "plural" })
      ).toEqual("singular");
    });

    it("should return the plural form when passing the subject as some else then 1", () => {
      expect(
        pluralize({ subject: 2, singular: "singular", plural: "plural" })
      ).toEqual("plural");
    });
  });

  describe("when passing an array", () => {
    it("should return the singular form when passing the subject as an array with one element", () => {
      expect(
        pluralize({ subject: [2], singular: "singular", plural: "plural" })
      ).toEqual("singular");
    });

    it("should return the plural form when passing the subject as an array with multiple items", () => {
      expect(
        pluralize({ subject: [0, 1], singular: "singular", plural: "plural" })
      ).toEqual("plural");
    });
  });

  describe("when using a different locale", () => {
    /**
     * French locales consider 0 as a singular form (whereas english based languages consider 0 as a plural form)
     */
    const locale = "fr-ca";

    beforeAll(() => {
      (
        Intl.PluralRules as unknown as jest.MockedFn<typeof Intl.PluralRules>
      ).mockRestore();
    });

    it("should return singular form when passing empty", () => {
      expect(
        pluralize({
          subject: [],
          singular: "singular",
          plural: "plural",
          locale,
        })
      ).toEqual("singular");

      expect(
        pluralize({
          subject: 0,
          singular: "singular",
          plural: "plural",
          locale,
        })
      ).toEqual("singular");
    });
  });
});
