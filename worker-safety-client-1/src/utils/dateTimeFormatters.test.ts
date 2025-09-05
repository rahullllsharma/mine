import {
  formatDateTime,
  formatDateOnly,
  formatTimeOnly,
} from "./dateTimeFormatters";

describe("dateTimeFormatters", () => {
  describe("formatDateTime", () => {
    it("should format a valid date time string correctly", () => {
      const result = formatDateTime("2024-01-15T14:30:00");
      expect(result).toContain("2024");
      expect(result).toContain("2:30 PM");
      expect(result).toContain(",");
    });

    it("should handle different date formats", () => {
      const result1 = formatDateTime("2024-12-25T09:15:00");
      expect(result1).toContain("2024");
      expect(result1).toContain("9:15 AM");
      expect(result1).toContain(",");

      const result2 = formatDateTime("2024-06-01T23:45:00");
      expect(result2).toContain("2024");
      expect(result2).toContain("11:45 PM");
      expect(result2).toContain(",");
    });

    it("should return original string for invalid date", () => {
      const result = formatDateTime("invalid-date");
      expect(result).toBe("invalid-date");
    });

    it("should handle empty string", () => {
      const result = formatDateTime("");
      expect(result).toBe("");
    });

    it("should handle null-like values", () => {
      const result = formatDateTime("null");
      expect(result).toBe("null");
    });

    it("should have comma separator between date and time", () => {
      const result = formatDateTime("2024-01-15T14:30:00");
      expect(result).toContain(",");
    });
  });

  describe("formatDateOnly", () => {
    it("should format a valid date string correctly", () => {
      const result = formatDateOnly("2024-01-15T14:30:00");
      expect(result).toBe("01/15/2024");
    });

    it("should handle different date formats", () => {
      const result1 = formatDateOnly("2024-12-25T09:15:00");
      expect(result1).toBe("12/25/2024");

      const result2 = formatDateOnly("2024-06-01T23:45:00");
      expect(result2).toBe("06/01/2024");
    });

    it("should return original string for invalid date", () => {
      const result = formatDateOnly("invalid-date");
      expect(result).toBe("invalid-date");
    });

    it("should handle empty string", () => {
      const result = formatDateOnly("");
      expect(result).toBe("");
    });

    it("should handle date-only strings", () => {
      const result = formatDateOnly("2024-01-15");
      expect(result).toBe("01/15/2024");
    });

    it("should handle single digit months and days with leading zeros", () => {
      const result = formatDateOnly("2024-03-05T10:00:00");
      expect(result).toBe("03/05/2024");
    });

    it("should handle double digit months and days", () => {
      const result = formatDateOnly("2024-12-25T10:00:00");
      expect(result).toBe("12/25/2024");
    });
  });

  describe("formatTimeOnly", () => {
    it("should format a valid time string correctly", () => {
      const result = formatTimeOnly("14:30");
      expect(result).toContain("2:30");
      expect(result).toContain("PM");
    });

    it("should handle different time formats", () => {
      const result1 = formatTimeOnly("09:15");
      expect(result1).toContain("9:15");
      expect(result1).toContain("AM");

      const result2 = formatTimeOnly("23:45");
      expect(result2).toContain("11:45");
      expect(result2).toContain("PM");

      const result3 = formatTimeOnly("00:00");
      expect(result3).toContain("12:00");
      expect(result3).toContain("AM");

      const result4 = formatTimeOnly("12:00");
      expect(result4).toContain("12:00");
      expect(result4).toContain("PM");
    });

    it("should return original string for invalid time", () => {
      const result = formatTimeOnly("invalid-time");
      expect(result).toBe("invalid-time");
    });

    it("should handle empty string", () => {
      const result = formatTimeOnly("");
      expect(result).toBe("");
    });

    it("should handle malformed time strings", () => {
      const result = formatTimeOnly("25:70");
      expect(result).toBe("25:70");
    });

    it("should handle single digit hours and minutes", () => {
      const result = formatTimeOnly("5:5");
      expect(result).toContain("5:05");
      expect(result).toContain("AM");
    });

    it("should handle edge case times", () => {
      const result1 = formatTimeOnly("00:00");
      expect(result1).toContain("12:00");
      expect(result1).toContain("AM");

      const result2 = formatTimeOnly("12:00");
      expect(result2).toContain("12:00");
      expect(result2).toContain("PM");
    });
  });

  describe("edge cases", () => {
    it("should handle very old dates", () => {
      const result = formatDateOnly("1900-01-01T00:00:00");
      expect(result).toBe("01/01/1900");
    });

    it("should handle future dates", () => {
      const result = formatDateOnly("2030-12-31T23:59:59");
      expect(result).toBe("12/31/2030");
    });

    it("should handle leap year dates", () => {
      const result = formatDateOnly("2024-02-29T12:00:00");
      expect(result).toBe("02/29/2024");
    });

    it("should handle timezone edge cases", () => {
      const result = formatTimeOnly("23:59");
      expect(result).toBe("11:59 PM");
    });
  });

  describe("function return types", () => {
    it("should return strings for all functions", () => {
      expect(typeof formatDateTime("2024-01-15T14:30:00")).toBe("string");
      expect(typeof formatDateOnly("2024-01-15T14:30:00")).toBe("string");
      expect(typeof formatTimeOnly("14:30")).toBe("string");
    });

    it("should handle error cases gracefully", () => {
      expect(typeof formatDateTime("invalid")).toBe("string");
      expect(typeof formatDateOnly("invalid")).toBe("string");
      expect(typeof formatTimeOnly("invalid")).toBe("string");
    });
  });
});
