import { convertDateToString, getDayRangeBetween } from "@/utils/date/helper";
import { getTimeFrame } from "./insights.utils";

describe(getTimeFrame.name, () => {
  it.each([
    { expectedDayCount: 7, input: 7 },
    { expectedDayCount: 14, input: 14 },
    { expectedDayCount: 14, input: -14 },
    { expectedDayCount: 30, input: -30 },
    { expectedDayCount: 90, input: -90 },
  ])(
    `Returns expectedDayCount days when called with timeFrame`,
    ({ expectedDayCount, input }) => {
      const [startDate, endDate] = getTimeFrame(input);
      const daysBetween = getDayRangeBetween(startDate, endDate);
      expect(expectedDayCount).toEqual(daysBetween.length);
    }
  );

  it("future timeframes include today", () => {
    const [startDate] = getTimeFrame(2);
    const today = convertDateToString();
    expect(today).toEqual(startDate);
  });

  it("past timeframes include today", () => {
    const [, endDate] = getTimeFrame(-2);
    const today = convertDateToString();
    expect(today).toEqual(endDate);
  });
});
