import { getDatesBoundaries } from "./dates.utils";

describe(getDatesBoundaries.name, () => {
  beforeEach(() => {
    jest.useFakeTimers();
    jest.setSystemTime(new Date("2022-01-03"));
  });

  it.each([
    {
      start: "",
      end: "2022-02-01",
      max: "2022-01-15",
      expected: {
        minStartDate: "2022-02-01",
        minEndDate: "2022-01-15",
      },
    },
    {
      start: "2022-01-01",
      end: "",
      max: "2022-01-15",
      expected: {
        minStartDate: undefined,
        minEndDate: "2022-01-15",
      },
    },
    {
      start: "2022-01-01",
      end: "2022-02-01",
      max: "",
      expected: {
        minEndDate: undefined,
        minStartDate: "2022-02-01",
      },
    },
    {
      start: "2022-01-01",
      end: "2022-02-01",
      max: "2022-01-15",
      expected: {
        minStartDate: "2022-02-01",
        minEndDate: "2022-01-15",
      },
    },
    {
      start: "-01-01", // fallbacks back to 2001
      end: "2022-02-01",
      max: "2022-01-15",
      expected: {
        minStartDate: "2022-02-01",
        minEndDate: "2022-01-15",
      },
    },
    {
      start: "2022-01-01",
      end: "-02-01", // fallbacks to 2001
      max: "2022-01-15",
      expected: {
        minStartDate: "2001-02-01",
        minEndDate: "2022-01-15",
      },
    },
  ])("should match the expected result", ({ start, end, max, expected }) => {
    expect(getDatesBoundaries(start, end, max)).toMatchObject(expected);
  });

  it("should return undefined when dates are not valid without a max date", () => {
    expect(getDatesBoundaries("invalid", "date", undefined)).toMatchObject({
      minStartDate: undefined,
      minEndDate: undefined,
    });
  });

  it("should return undefined when dates are not valid with a max date", () => {
    expect(getDatesBoundaries("invalid", "date", "2022-01-01")).toMatchObject({
      minStartDate: undefined,
      minEndDate: undefined,
    });
  });
});
