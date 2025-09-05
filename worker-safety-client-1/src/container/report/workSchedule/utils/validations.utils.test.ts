import { greaterThanDate, greaterThanTimeSameDay } from "./validations.utils";

describe("validations", () => {
  const prevDate = "2022-01-01";
  const futureDate = "2022-02-01";

  describe("greaterThanDate", () => {
    it("should be valid when start date is less than end date", () => {
      expect(greaterThanDate({ start: prevDate, end: futureDate })).toBe(true);
    });

    it("should be valid when start date is equal to the end date", () => {
      expect(greaterThanDate({ start: prevDate, end: prevDate })).toBe(true);
    });

    it.each`
      startDate       | endDate
      ${undefined}    | ${"2022-01-01"}
      ${"2022-01-01"} | ${undefined}
    `(
      "should skip validation (by returning true) one of the required dates are not filled",
      ({ startDate, endDate }) => {
        expect(greaterThanDate({ start: startDate, end: endDate })).toBe(true);
      }
    );

    it("should return an error when start date is greater than end date", () => {
      expect(greaterThanDate({ start: futureDate, end: prevDate })).toBe(false);
    });

    describe.each(["", "xpto", "10:20"])(
      "when has invalid parameter is = %s",
      invalid => {
        it("should return an error message when the START DATE parameter is invalid", () => {
          // eslint-disable-next-line @typescript-eslint/ban-ts-comment
          // @ts-ignore
          expect(greaterThanDate({ start: invalid, end: prevDate })).toBe(
            false
          );
        });

        it("should return an error message when the END DATE parameter is invalid", () => {
          // eslint-disable-next-line @typescript-eslint/ban-ts-comment
          // @ts-ignore
          expect(greaterThanDate({ start: prevDate, end: invalid })).toBe(
            false
          );
        });
      }
    );
  });

  describe("greaterThanTimeSameDay", () => {
    const prevTime = "08:00";
    const futureTime = "11:00";

    const params = {
      startDate: prevDate,
      startTime: prevTime,
      endDate: prevDate,
      endTime: futureTime,
    };

    it("should be valid when not on the SAME day", () => {
      expect(greaterThanTimeSameDay({ ...params, endDate: futureDate })).toBe(
        true
      );
    });

    it("should be valid when start time is less than end time", () => {
      expect(
        greaterThanTimeSameDay({
          ...params,
        })
      ).toBe(true);
    });

    it("should be valid when start time is less equal to end time", () => {
      expect(
        greaterThanTimeSameDay({
          ...params,
          endTime: prevTime,
        })
      ).toBe(true);
    });

    it.each([
      { ...params, startDate: undefined },
      { ...params, startTime: undefined },
      { ...params, endDate: undefined },
      { ...params, endTime: undefined },
    ])(
      "should skip validation (by returning true) one of the required dates are not filled",
      overwritten => {
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        expect(greaterThanTimeSameDay(overwritten)).toBe(true);
      }
    );

    describe.each(["", "xpto"])(
      "when has invalid parameter is = %s",
      invalid => {
        it("should return an error message when the START DATE parameter is invalid", () => {
          expect(
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            greaterThanTimeSameDay({ ...params, startDate: invalid })
          ).toBe(false);
        });

        it("should return an error message when the START TIME parameter is invalid", () => {
          expect(
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            greaterThanTimeSameDay({ ...params, startTime: invalid })
          ).toBe(false);
        });

        it("should return an error message when the END DATE parameter is invalid", () => {
          expect(
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            greaterThanTimeSameDay({ ...params, endDate: invalid })
          ).toBe(false);
        });

        it("should return an error message when the END TIME parameter is invalid", () => {
          expect(
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            greaterThanTimeSameDay({ ...params, endTime: invalid })
          ).toBe(false);
        });
      }
    );
  });
});
