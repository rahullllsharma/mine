import {
  checkIsToday,
  convertDateToString,
  convertToDate,
  formatRelativeOrAbsoluteDate,
  formatTimeHoursAndMinutes,
  getDate,
  getDayAndWeekdayFromDate,
  getDayRange,
  getEarliestDate,
  getFormattedDate,
  getFormattedLocaleDateTime,
  getGenerationDate,
  isDateValid,
  isDateWithinRange,
  isFollowingDate,
  isPreviousDate,
  isSameDate,
} from "./helper";

describe("Calendar Helper", () => {
  describe(convertToDate.name, () => {
    it.each([null, "", "29-04-2001 10:30", "29-04-2001T10:20"])(
      "should thrown an error",
      date => {
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        expect(() => convertToDate(date)).toThrowError(
          `Invalid Date = ${date}`
        );
      }
    );

    it.each([
      { date: "2000-01-01", expected: "2000-01-01T00:00:00.000Z" },
      { date: "04/04/2002", expected: "2002-04-04T00:00:00.000Z" },
      { date: "05/05/2020 10:20", expected: "2020-05-05T10:20:00.000Z" },
    ])("should parse the date correctly", ({ date, expected }) => {
      expect(convertToDate(date)).toEqual(new Date(expected));
    });
  });

  describe("getFormattedDate", () => {
    it("should return a formatted with long month format", () => {
      const date = "2022-10-10";
      expect(getFormattedDate(date, "long")).toEqual("October 10, 2022");
    });

    it("should return a formatted with short month format", () => {
      const date = "2022-10-10";
      expect(getFormattedDate(date, "short")).toEqual("Oct 10, 2022");
    });
  });

  describe("isDateValid", () => {
    it('should return "true" if the date is valid', () => {
      expect(isDateValid("2022-10-05")).toBeTruthy();
    });

    it('should return "false" if the date is invalid', () => {
      expect(isDateValid("invalid date")).toBeFalsy();
    });
  });

  describe("checkIsToday", () => {
    it("should return true if the given date matches the current date", () => {
      const isToday = checkIsToday(new Date().toString());
      expect(isToday).toBeTruthy();
    });

    it("should return false if the given date does not match the current date", () => {
      const isToday = checkIsToday("2021-01-01");
      expect(isToday).toBeFalsy();
    });

    it("should return false if the date is invalid", () => {
      const isToday = checkIsToday("invalid date");
      expect(isToday).toBeFalsy();
    });
  });

  describe("isSameDate", () => {
    it('should return "true" if the dates match', () => {
      const date1 = new Date();
      const date2 = new Date();
      expect(isSameDate(date1, date2)).toBeTruthy();
    });

    it('should return "false" if the dates don"t match', () => {
      const date1 = new Date();
      const date2 = new Date(new Date().getTime() + 24 * 60 * 60 * 1000);
      expect(isSameDate(date1, date2)).toBeFalsy();
    });
  });

  describe("getDayAndWeekdayFromDate", () => {
    it("should return a day and a weekday of a given date", () => {
      const [day, weekday] = getDayAndWeekdayFromDate("2022-01-20");
      expect(day).toBe("20");
      expect(weekday).toBe("Thu");
    });

    it("should return empty values if a date is invalid", () => {
      const [day, weekday] = getDayAndWeekdayFromDate("invalid date");
      expect(day).toBe("");
      expect(weekday).toBe("");
    });
  });

  describe("getDate", () => {
    it("should return a earlier date based on the number of days to decrement", () => {
      const day = getDate("2022-10-20", -5);
      expect(day).toEqual("2022-10-15");
    });

    it("should return a later date based on the number of days to increment", () => {
      const day = getDate("2022-10-20", 5);
      expect(day).toEqual("2022-10-25");
    });

    it("should return one day fewer if {includeToday: true} is passed (incrementing)", () => {
      let day = getDate("2022-10-20", 5, { includeToday: false });
      expect(day).toEqual("2022-10-25");
      day = getDate("2022-10-20", 5, { includeToday: true });
      expect(day).toEqual("2022-10-24");
    });

    it("should return one day fewer if {includeToday: true} is passed (decrementing)", () => {
      let day = getDate("2022-10-20", -5, { includeToday: false });
      expect(day).toEqual("2022-10-15");

      day = getDate("2022-10-20", -5, { includeToday: true });
      expect(day).toEqual("2022-10-16");
    });
  });

  describe("getDayRange", () => {
    it("should return a date range based on a reference day and the number of days to increment and decrement", () => {
      const startingDay = 17;
      const mockList = [];
      for (let i = 0; i <= 6; i++) {
        mockList.push(`2022-10-${startingDay + i}`);
      }

      const referenceDay = "2022-10-20";
      const list = getDayRange(referenceDay, 3, 3);

      expect(list).toEqual(mockList);
    });
  });

  describe("isPreviousDate", () => {
    it("should return true if the give date is earlier than the reference date", () => {
      expect(isPreviousDate("2022-01-10", "2022-01-20")).toBeTruthy();
    });

    it("should return false if the give date is not earlier than the reference date", () => {
      expect(isPreviousDate("2022-01-25", "2022-01-20")).toBeFalsy();
    });
  });

  describe("isFollowingDate", () => {
    it("should return true if the give date is later than the reference date", () => {
      expect(isFollowingDate("2022-01-25", "2022-01-20")).toBeTruthy();
    });

    it("should return false if the give date is not later than the reference date", () => {
      expect(isFollowingDate("2022-01-10", "2022-01-20")).toBeFalsy();
    });
  });

  describe("isDateWithinRange", () => {
    const startDate = "2022-01-10";
    const endDate = "2022-01-20";

    it('should return "true" if the given date is within the date range', () => {
      const date = "2022-01-15";
      expect(isDateWithinRange(startDate, endDate, date)).toBeTruthy();
    });

    it('should return "false" if the given date occurs before the start date', () => {
      const date = "2022-01-05";
      expect(isDateWithinRange(startDate, endDate, date)).toBeFalsy();
    });

    it('should return "false" if the given date occurs after the end date', () => {
      const date = "2022-01-25";
      expect(isDateWithinRange(startDate, endDate, date)).toBeFalsy();
    });
  });

  describe("convertDateToString", () => {
    beforeEach(() => {
      jest.useFakeTimers();
      jest.setSystemTime(new Date("2022-01-20").valueOf());
    });

    it("by default, it sets a new Date and outputs as yyyy-mm-dd format", () => {
      expect(convertDateToString()).toEqual("2022-01-20");
    });

    it('should receive a date and convert it to a string with the "yyyy-mm-dd" format', () => {
      const date = new Date("2022-01-20");
      expect(convertDateToString(date)).toEqual("2022-01-20");
    });

    describe("when date and time are UTC", () => {
      it("should have the same date", () => {
        const date = new Date(Date.UTC(2022, 0, 3, 15, 0, 0)).toLocaleString(
          "en-US",
          { timeZone: "UTC" }
        );
        expect(convertDateToString(date)).toEqual("2022-01-03");
      });
    });

    describe("when date and time are PST", () => {
      it("should have the same date", () => {
        const date = new Date(Date.UTC(2022, 0, 3, 15, 0, 0)).toLocaleString(
          "en-US",
          { timeZone: "America/Los_Angeles" }
        );
        expect(convertDateToString(date)).toEqual("2022-01-03");
      });
    });

    describe("when date and time are EST", () => {
      it("should have the same date", () => {
        const date = new Date(Date.UTC(2022, 0, 3, 15, 0, 0)).toLocaleString(
          "en-US",
          { timeZone: "America/New_York" }
        );
        expect(convertDateToString(date)).toEqual("2022-01-03");
      });
    });
    describe("when date and time are CET", () => {
      it("should have the same date", () => {
        const date = new Date(Date.UTC(2022, 0, 3, 15, 0, 0)).toLocaleString(
          "en-US",
          { timeZone: "Europe/Moscow" }
        );
        expect(convertDateToString(date)).toEqual("2022-01-03");
      });
    });
  });

  describe("formatTimeHoursAndMinutes", () => {
    it.each([undefined, null, {}, 1])(
      "should return undefined when not a valid string was provided",
      param => {
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        expect(formatTimeHoursAndMinutes(param)).toBeUndefined();
      }
    );

    it.each(["1932", "abcc", "2022-10-01"])(
      "should return undefined when an invalid time was provided",
      param => {
        expect(formatTimeHoursAndMinutes(param)).toBeUndefined();
      }
    );

    it.each(["20:20:00.3192184", "20:20:50", "20:20"])(
      "should format and return the time with only hours and minutes",
      param => {
        expect(formatTimeHoursAndMinutes(param)).toEqual("20:20");
      }
    );
  });

  describe("getEarliestDate", () => {
    it.each([
      { sample: ["2022-01-01"], expected: "2022-01-01" },
      { sample: ["2022-01-01", "2022-01-02"], expected: "2022-01-02" },
      { sample: ["2022-01-01", "2022-01-01"], expected: "2022-01-01" },
      { sample: ["2022-01-02", "2022-01-01"], expected: "2022-01-02" },
      {
        sample: ["2022-01-02", "2022-02-01", "2022-01-04", "2022-01-05"],
        expected: "2022-02-01",
      },
    ])("should return the oldest date", ({ sample, expected }) => {
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      expect(getEarliestDate(...sample)).toEqual(new Date(expected));
    });
  });

  describe("getFormattedLocaleDateTime", () => {
    it.each([
      "2022-05-03T15:14:43.123Z",
      "2022-05-03T15:14",
      "2022-05-03 15:14",
      "2022-05-03T16:14:00.000+0100",
    ])(
      "should return a string formatted as yyyy-dd-mmThh:mm from a date",
      date => {
        expect(getFormattedLocaleDateTime(date)).toEqual("2022-05-03T15:14");
      }
    );

    it.each([null, undefined, ""])(
      "should return false when it is not possible to format the date",
      date => {
        expect(getFormattedLocaleDateTime(date as string)).toBe("");
      }
    );

    describe("when the time parameter is passed", () => {
      it("should return the formatted date and override the time", () => {
        const date = "2022-05-03T15:14";
        expect(
          getFormattedLocaleDateTime(date, {
            time: "00:00",
          })
        ).toEqual("2022-05-03T00:00");
      });

      it.each([undefined, null, 1, "11-22", "111:333", "99:99"])(
        "should return the formatted date and ignore the time if not properly formatted",
        time => {
          const date = "2022-05-03T15:14";
          expect(
            getFormattedLocaleDateTime(date, {
              time: time as string,
            })
          ).toEqual("2022-05-03T15:14");
        }
      );
    });
  });

  describe("getGenerationDate", () => {
    beforeEach(() => {
      jest.useFakeTimers();
      jest.setSystemTime(new Date("2022-07-25T10:24:55").valueOf());
    });

    it("should parse in the correct format", () => {
      expect(getGenerationDate()).toEqual("7/25/22, 10:24:55 AM UTC");
    });
  });

  describe("formatRelativeOrAbsoluteDate", () => {
    beforeEach(() => {
      jest.useFakeTimers();
      // Set current time to 2023-12-25T12:00:00Z for consistent testing
      jest.setSystemTime(new Date("2023-12-25T12:00:00Z").valueOf());
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    describe("Input validation", () => {
      it("should return empty string for empty input", () => {
        expect(formatRelativeOrAbsoluteDate("")).toBe("");
      });

      it("should return empty string for invalid date string", () => {
        expect(formatRelativeOrAbsoluteDate("invalid-date")).toBe("");
      });

      it("should return empty string for malformed ISO date", () => {
        expect(formatRelativeOrAbsoluteDate("2023-13-45")).toBe("");
      });
    });

    describe("Relative time formatting (< 24 hours)", () => {
      it("should return 'just now' for very recent dates (< 1 minute)", () => {
        // 30 seconds ago
        const thirtySecondsAgo = new Date("2023-12-25T11:59:30Z").toISOString();
        expect(formatRelativeOrAbsoluteDate(thirtySecondsAgo)).toBe("just now");
      });

      it("should return abbreviated minutes for dates within the last hour", () => {
        // 15 minutes ago
        const fifteenMinutesAgo = new Date(
          "2023-12-25T11:45:00Z"
        ).toISOString();
        expect(formatRelativeOrAbsoluteDate(fifteenMinutesAgo)).toBe(
          "15 min ago"
        );

        // 45 minutes ago
        const fortyFiveMinutesAgo = new Date(
          "2023-12-25T11:15:00Z"
        ).toISOString();
        expect(formatRelativeOrAbsoluteDate(fortyFiveMinutesAgo)).toBe(
          "45 min ago"
        );

        // 1 minute ago
        const oneMinuteAgo = new Date("2023-12-25T11:59:00Z").toISOString();
        expect(formatRelativeOrAbsoluteDate(oneMinuteAgo)).toBe("1 min ago");
      });

      it("should return abbreviated hours for dates within the last 24 hours", () => {
        // 2 hours ago
        const twoHoursAgo = new Date("2023-12-25T10:00:00Z").toISOString();
        expect(formatRelativeOrAbsoluteDate(twoHoursAgo)).toBe("2 hr ago");

        // 12 hours ago
        const twelveHoursAgo = new Date("2023-12-25T00:00:00Z").toISOString();
        expect(formatRelativeOrAbsoluteDate(twelveHoursAgo)).toBe("12 hr ago");

        // 23 hours ago (just under 24h threshold)
        const twentyThreeHoursAgo = new Date(
          "2023-12-24T13:00:00Z"
        ).toISOString();
        expect(formatRelativeOrAbsoluteDate(twentyThreeHoursAgo)).toBe(
          "23 hr ago"
        );
      });

      it("should handle future dates within 24 hours", () => {
        // 30 minutes in the future
        const thirtyMinutesFuture = new Date(
          "2023-12-25T12:30:00Z"
        ).toISOString();
        expect(formatRelativeOrAbsoluteDate(thirtyMinutesFuture)).toBe(
          "in 30 min"
        );

        // 5 hours in the future
        const fiveHoursFuture = new Date("2023-12-25T17:00:00Z").toISOString();
        expect(formatRelativeOrAbsoluteDate(fiveHoursFuture)).toBe("in 5 hr");

        // 23 hours in the future
        const twentyThreeHoursFuture = new Date(
          "2023-12-26T11:00:00Z"
        ).toISOString();
        expect(formatRelativeOrAbsoluteDate(twentyThreeHoursFuture)).toBe(
          "in 23 hr"
        );
      });
    });

    describe("Absolute date formatting (>= 24 hours)", () => {
      it("should return YYYY-MM-DD format for dates exactly 24 hours ago", () => {
        const twentyFourHoursAgo = new Date(
          "2023-12-24T12:00:00Z"
        ).toISOString();
        expect(formatRelativeOrAbsoluteDate(twentyFourHoursAgo)).toBe(
          "2023-12-24"
        );
      });

      it("should return YYYY-MM-DD format for dates more than 24 hours ago", () => {
        // 25 hours ago
        const twentyFiveHoursAgo = new Date(
          "2023-12-24T11:00:00Z"
        ).toISOString();
        expect(formatRelativeOrAbsoluteDate(twentyFiveHoursAgo)).toBe(
          "2023-12-24"
        );

        // 3 days ago
        const threeDaysAgo = new Date("2023-12-22T12:00:00Z").toISOString();
        expect(formatRelativeOrAbsoluteDate(threeDaysAgo)).toBe("2023-12-22");

        // 1 month ago
        const oneMonthAgo = new Date("2023-11-25T12:00:00Z").toISOString();
        expect(formatRelativeOrAbsoluteDate(oneMonthAgo)).toBe("2023-11-25");

        // 1 year ago
        const oneYearAgo = new Date("2022-12-25T12:00:00Z").toISOString();
        expect(formatRelativeOrAbsoluteDate(oneYearAgo)).toBe("2022-12-25");
      });

      it("should return YYYY-MM-DD format for future dates more than 24 hours away", () => {
        // 25 hours in the future
        const twentyFiveHoursFuture = new Date(
          "2023-12-26T13:00:00Z"
        ).toISOString();
        expect(formatRelativeOrAbsoluteDate(twentyFiveHoursFuture)).toBe(
          "2023-12-26"
        );

        // 1 week in the future
        const oneWeekFuture = new Date("2024-01-01T12:00:00Z").toISOString();
        expect(formatRelativeOrAbsoluteDate(oneWeekFuture)).toBe("2024-01-01");
      });
    });

    describe("Edge cases", () => {
      it("should handle dates exactly at the 24-hour boundary", () => {
        // Exactly 24 hours ago
        const exactlyTwentyFourHoursAgo = new Date(
          "2023-12-24T12:00:00Z"
        ).toISOString();
        expect(formatRelativeOrAbsoluteDate(exactlyTwentyFourHoursAgo)).toBe(
          "2023-12-24"
        );

        // Exactly 24 hours in the future
        const exactlyTwentyFourHoursFuture = new Date(
          "2023-12-26T12:00:00Z"
        ).toISOString();
        expect(formatRelativeOrAbsoluteDate(exactlyTwentyFourHoursFuture)).toBe(
          "2023-12-26"
        );
      });

      it("should handle leap year dates", () => {
        // Set current time to leap year
        jest.setSystemTime(new Date("2024-02-29T12:00:00Z").valueOf());

        const yesterday = new Date("2024-02-28T12:00:00Z").toISOString();
        expect(formatRelativeOrAbsoluteDate(yesterday)).toBe("2024-02-28");
      });

      it("should handle year boundary crossings", () => {
        // Set current time to New Year's Day
        jest.setSystemTime(new Date("2024-01-01T12:00:00Z").valueOf());

        const lastYear = new Date("2023-12-31T12:00:00Z").toISOString();
        expect(formatRelativeOrAbsoluteDate(lastYear)).toBe("2023-12-31");

        const lastYearWithinDay = new Date(
          "2023-12-31T16:00:00Z"
        ).toISOString();
        expect(formatRelativeOrAbsoluteDate(lastYearWithinDay)).toBe(
          "20 hr ago"
        );
      });

      it("should handle timezone-aware ISO strings", () => {
        // Date with timezone offset
        const dateWithTimezone = "2023-12-25T10:00:00+02:00"; // 8:00 UTC, 4 hours ago
        expect(formatRelativeOrAbsoluteDate(dateWithTimezone)).toBe("4 hr ago");
      });
    });

    describe("Error handling", () => {
      it("should handle dates that cause parsing errors gracefully", () => {
        // Mock console.error to avoid polluting test output
        const consoleSpy = jest.spyOn(console, "error").mockImplementation();

        // Test various malformed dates
        expect(formatRelativeOrAbsoluteDate("not-a-date")).toBe("");
        expect(formatRelativeOrAbsoluteDate("2023-99-99")).toBe("");
        expect(formatRelativeOrAbsoluteDate("2023-12-32T25:61:61Z")).toBe("");

        expect(consoleSpy).toHaveBeenCalled();
        consoleSpy.mockRestore();
      });

      it("should handle very old dates", () => {
        const veryOldDate = new Date("1900-01-01T00:00:00Z").toISOString();
        expect(formatRelativeOrAbsoluteDate(veryOldDate)).toBe("1900-01-01");
      });

      it("should handle very far future dates", () => {
        const veryFarFuture = new Date("2100-12-31T23:59:59Z").toISOString();
        expect(formatRelativeOrAbsoluteDate(veryFarFuture)).toBe("2100-12-31");
      });
    });

    describe("Real-world scenarios", () => {
      it("should handle typical API response date formats", () => {
        // Common ISO formats from APIs
        const apiDate1 = "2023-12-25T10:30:45.123Z";
        expect(formatRelativeOrAbsoluteDate(apiDate1)).toBe("1 hr ago");

        const apiDate2 = "2023-12-25T11:45:30.000Z";
        expect(formatRelativeOrAbsoluteDate(apiDate2)).toBe("15 min ago");

        const apiDate3 = "2023-12-23T12:00:00.000Z";
        expect(formatRelativeOrAbsoluteDate(apiDate3)).toBe("2023-12-23");
      });

      it("should handle consistent formatting for similar time differences", () => {
        // Test that similar times produce consistent results with proper rounding
        const date1 = new Date("2023-12-25T11:30:00Z").toISOString(); // 30 min ago
        const date2 = new Date("2023-12-25T11:30:30Z").toISOString(); // 29.5 min ago (rounds to 30)

        expect(formatRelativeOrAbsoluteDate(date1)).toBe("30 min ago");
        expect(formatRelativeOrAbsoluteDate(date2)).toBe("30 min ago"); // 29.5 rounds to 30
      });
    });
  });
});
