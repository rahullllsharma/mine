import { screen, render } from "@testing-library/react";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import RiskLabel from "./RiskLabel";

describe(RiskLabel.name, () => {
  const progressiveRiskLevels = Object.values(RiskLevel).filter(
    risk => risk !== RiskLevel.UNKNOWN && risk !== RiskLevel.RECALCULATING
  );
  describe.each(progressiveRiskLevels)(`when risk level is %s`, level => {
    it(`should contain className corresponding to '${level}'`, () => {
      render(<RiskLabel risk={level} label="some label" />);
      const labelElement: HTMLElement = screen.getByRole("note");
      expect(labelElement.classList.value).toMatch(
        new RegExp(`text-risk-${level}`, "i")
      );
    });
  });

  describe.each([RiskLevel.UNKNOWN, RiskLevel.RECALCULATING])(
    `when risk level is %s`,
    level => {
      it('should contain className corresponding to "text-neutral-shade-75"', () => {
        render(<RiskLabel risk={level} label="some label" />);
        const labelElement: HTMLElement = screen.getByRole("note");
        expect(labelElement.classList.value).toMatch(/text-neutral-shade-75/i);
      });
    }
  );
});
