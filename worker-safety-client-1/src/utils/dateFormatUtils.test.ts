import { getPlaceholder, getDisplayFormat } from "./dateFormatUtils";

// Mock navigator for testing
const mockNavigator = {
  language: "en-US",
};

// Store original navigator
const originalNavigator = global.navigator;

describe("dateFormatUtils", () => {
  beforeEach(() => {
    // Mock navigator globally
    global.navigator = mockNavigator as any;
  });

  afterEach(() => {
    // Restore original navigator
    global.navigator = originalNavigator;
    jest.clearAllMocks();
  });

  describe("getPlaceholder", () => {
    beforeEach(() => {
      global.navigator = { language: "en-US" } as any;
    });

    it("should return a placeholder for date type", () => {
      const placeholder = getPlaceholder("date");
      expect(typeof placeholder).toBe("string");
      expect(placeholder).toMatch(/[MDY\/\-\.]+/);
    });

    it("should return HH:mm for time type", () => {
      const placeholder = getPlaceholder("time");
      expect(placeholder).toBe("HH:mm");
    });

    it("should return a datetime placeholder for datetime-local type", () => {
      const placeholder = getPlaceholder("datetime-local");
      expect(typeof placeholder).toBe("string");
      expect(placeholder).toMatch(/[MDYHm:\/\-\.\s]+/);
    });
  });

  describe("getDisplayFormat", () => {
    beforeEach(() => {
      global.navigator = { language: "en-US" } as any;
    });

    it("should return a display format for date type", () => {
      const format = getDisplayFormat("date");
      expect(typeof format).toBe("string");
      expect(format).toMatch(/[MDY\/\-\.]+/);
    });

    it("should return hh:mm A for time type", () => {
      const format = getDisplayFormat("time");
      expect(format).toBe("hh:mm A");
    });

    it("should return a datetime display format for datetime-local type", () => {
      const format = getDisplayFormat("datetime-local");
      expect(typeof format).toBe("string");
      expect(format).toMatch(/[MDYhmA:\/\-\.\s]+/);
    });
  });

  describe("locale-specific behavior", () => {
    it("should handle different locales consistently", () => {
      const locales = ["en-US", "en-GB", "fr-FR", "de-DE"];

      locales.forEach(locale => {
        global.navigator = { language: locale } as any;

        // All functions should return strings
        expect(typeof getPlaceholder("date")).toBe("string");
        expect(typeof getDisplayFormat("date")).toBe("string");

        // Time formats should be consistent
        expect(getPlaceholder("time")).toBe("HH:mm");
        expect(getDisplayFormat("time")).toBe("hh:mm A");
      });
    });
  });
});
