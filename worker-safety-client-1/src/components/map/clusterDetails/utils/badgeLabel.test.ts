import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { getLabelWithRiskIcon } from "./badgeLabel";

describe.each`
  risk                 | label        | expected
  ${undefined}         | ${undefined} | ${""}
  ${RiskLevel.LOW}     | ${undefined} | ${""}
  ${RiskLevel.UNKNOWN} | ${undefined} | ${""}
  ${RiskLevel.LOW}     | ${"1"}       | ${"1"}
  ${RiskLevel.UNKNOWN} | ${"1"}       | ${"? 1"}
`("getLabelWithRiskIcon", ({ risk, label, expected }) => {
  it("should match $expected for $risk and $label", () => {
    expect(getLabelWithRiskIcon({ risk, label })).toEqual(expected);
  });
});
