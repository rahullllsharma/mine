import { RiskLevel } from "@/api/generated/types";
import { RiskLevel as RiskBadgeRiskLevel } from "@/components/riskBadge/RiskLevel";
import {
  getBackgroundColorByRiskLevel,
  getDefaultTextColorByRiskLevel,
  getRiskIcon,
  getBorderColorByRiskLevel,
  convertRiskLevelToRiskBadgeRiskLevel,
} from "./utils";

describe("Risk Utils", () => {
  const bgByRiskLevel = [
    { risk: RiskLevel.High, expected: "bg-risk-high" },
    { risk: RiskLevel.Medium, expected: "bg-risk-medium" },
    { risk: RiskLevel.Low, expected: "bg-risk-low" },
    { risk: RiskLevel.Unknown, expected: "bg-risk-unknown" },
    { risk: RiskLevel.Recalculating, expected: "bg-risk-recalculating" },
  ];

  const textColorByRiskLevel = [
    { risk: RiskLevel.High, expected: "text-white" },
    { risk: RiskLevel.Medium, expected: "text-neutral-shade-100" },
    { risk: RiskLevel.Low, expected: "text-white" },
    { risk: RiskLevel.Unknown, expected: "text-neutral-shade-75" },
    { risk: RiskLevel.Recalculating, expected: "text-neutral-shade-75" },
  ];
  const riskIcon = [
    { risk: RiskLevel.High, expected: "chevron_up" },
    { risk: RiskLevel.Medium, expected: "tilde" },
    { risk: RiskLevel.Low, expected: "chevron_down" },
    { risk: RiskLevel.Unknown, expected: undefined },
    { risk: RiskLevel.Recalculating, expected: undefined },
  ];
  const borderColor = [
    { risk: RiskLevel.High, expected: "border-risk-high" },
    { risk: RiskLevel.Medium, expected: "border-risk-medium" },
    { risk: RiskLevel.Low, expected: "border-risk-low" },
    { risk: RiskLevel.Unknown, expected: "border-risk-unknown" },
    { risk: RiskLevel.Recalculating, expected: "" },
  ];

  const riskLevels = [
    { risk: RiskLevel.High, expected: RiskBadgeRiskLevel.HIGH },
    { risk: RiskLevel.Medium, expected: RiskBadgeRiskLevel.MEDIUM },
    { risk: RiskLevel.Low, expected: RiskBadgeRiskLevel.LOW },
    { risk: RiskLevel.Unknown, expected: RiskBadgeRiskLevel.UNKNOWN },
    {
      risk: RiskLevel.Recalculating,
      expected: RiskBadgeRiskLevel.RECALCULATING,
    },
  ];

  test.each(bgByRiskLevel)(
    "$risk should have $expected background className",
    ({ risk, expected }) => {
      expect(getBackgroundColorByRiskLevel(risk)).toEqual(expected);
    }
  );

  test.each(textColorByRiskLevel)(
    "$risk should have text color className $expected",
    ({ risk, expected }) => {
      expect(getDefaultTextColorByRiskLevel(risk)).toEqual(expected);
    }
  );

  test.each(riskIcon)(
    "$risk should have $expected icon",
    ({ risk, expected }) => {
      expect(getRiskIcon(risk)).toEqual(expected);
    }
  );

  test.each(borderColor)(
    "$risk should have $expected border className",
    ({ risk, expected }) => {
      expect(getBorderColorByRiskLevel(risk)).toEqual(expected);
    }
  );

  test.each(riskLevels)(
    "$risk should have $expected risk badge risk level",
    ({ risk, expected }) => {
      expect(convertRiskLevelToRiskBadgeRiskLevel(risk)).toEqual(expected);
    }
  );
});
