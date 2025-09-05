import { shuffle } from "lodash";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { prepChartData } from "./charts.utils";

describe("prepChartData", () => {
  describe("receives an empty list", () => {
    it("returns a list with an entry per date", () => {
      const data = prepChartData([], "2022-01-09", "2022-01-11");
      expect(data).toStrictEqual([
        { date: "1/9/22" },
        { date: "1/10/22" },
        { date: "1/11/22" },
      ]);
    });

    it("wraps months as expected", () => {
      const data = prepChartData([], "2022-02-27", "2022-03-02");
      expect(data).toStrictEqual([
        { date: "2/27/22" },
        { date: "2/28/22" },
        { date: "3/1/22" },
        { date: "3/2/22" },
      ]);
    });
  });

  describe("receives riskCounts", () => {
    // the 09th and 10th are used to show that sorting must be done by date,
    // not by string
    const inputData = [
      {
        date: "2022-01-09",
        riskLevel: RiskLevel.HIGH,
        count: 10,
      },
      {
        date: "2022-01-09",
        riskLevel: RiskLevel.MEDIUM,
        count: 20,
      },
      {
        date: "2022-01-09",
        riskLevel: RiskLevel.LOW,
        count: 30,
      },
      {
        date: "2022-01-10",
        riskLevel: RiskLevel.HIGH,
        count: 5,
      },
      {
        date: "2022-01-10",
        riskLevel: RiskLevel.MEDIUM,
        count: 10,
      },
      {
        date: "2022-01-10",
        riskLevel: RiskLevel.LOW,
        count: 20,
      },
      {
        date: "2022-01-11",
        riskLevel: RiskLevel.HIGH,
        count: 1,
      },
      // skipping medium
      {
        date: "2022-01-11",
        riskLevel: RiskLevel.LOW,
        // set Low to zero
        count: 0,
      },
    ];

    const expectedOutput = [
      {
        date: "1/9/22",
        High: 10,
        Medium: 20,
        Low: 30,
      },
      {
        date: "1/10/22",
        High: 5,
        Medium: 10,
        Low: 20,
      },
      {
        date: "1/11/22",
        High: 1,
        // No 'Medium' included
        // No 'Low' b/c zeros are not set
      },
    ];

    it("groups by date, merges counts, formats the date, sets the order", () => {
      expect(
        prepChartData(inputData, "2022-01-09", "2022-01-11")
      ).toStrictEqual(expectedOutput);

      // should work for any order
      const shuffled = shuffle(inputData);
      expect(prepChartData(shuffled, "2022-01-09", "2022-01-11")).toStrictEqual(
        expectedOutput
      );

      const shuffledTwice = shuffle(shuffled);
      expect(
        prepChartData(shuffledTwice, "2022-01-09", "2022-01-11")
      ).toStrictEqual(expectedOutput);
    });

    it("fills in missing dates", () => {
      const newExpectedOutput = [...expectedOutput, { date: "1/12/22" }];

      expect(
        prepChartData(inputData, "2022-01-09", "2022-01-12")
      ).toStrictEqual(newExpectedOutput);
    });
  });

  describe("receives a missing start or end date", () => {
    it("returns an empty list", () => {
      const inputData = [
        {
          date: "2022-01-09",
          riskLevel: RiskLevel.HIGH,
          count: 10,
        },
      ];

      expect(
        prepChartData(inputData, "2022-01-09", "2022-01-09")
      ).toStrictEqual([
        {
          High: 10,
          date: "1/9/22",
        },
      ]);

      expect(prepChartData(inputData, undefined, "2022-01-09")).toStrictEqual(
        []
      );
      expect(prepChartData(inputData, "2022-01-09", undefined)).toStrictEqual(
        []
      );
    });
  });
});
