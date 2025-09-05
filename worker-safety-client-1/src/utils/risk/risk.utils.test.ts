import type { IconName } from "@urbint/silica";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import {
  getBackgroundColorByRiskLevel,
  getBorderColorByRiskLevel,
  getDefaultTextColorByRiskLevel,
  getLocationRiskIconBackgroundColorByRiskLevel,
  getRiskIcon,
  getTextColorByRiskLevel,
} from "./risk.utils";

const riskLevels = Object.values(RiskLevel).filter(
  risk => risk !== RiskLevel.RECALCULATING
);

const riskIcons: Record<RiskLevel, IconName | undefined> = {
  [RiskLevel.HIGH]: "chevron_up",
  [RiskLevel.MEDIUM]: "tilde",
  [RiskLevel.LOW]: "chevron_down",
  [RiskLevel.UNKNOWN]: undefined,
  [RiskLevel.RECALCULATING]: undefined,
};

describe("risk helper", () => {
  describe.each(riskLevels)(`when risk level is %s`, level => {
    it(`should return the background risk-${level} color`, () => {
      expect(getBackgroundColorByRiskLevel(level)).toMatch(
        new RegExp(`bg-risk-${level}`, "i")
      );
    });

    it(`should return the border risk-${level} color`, () => {
      expect(getBorderColorByRiskLevel(level)).toMatch(
        new RegExp(`border-risk-${level}`, "i")
      );
    });

    it(`should return the border risk-${level} color`, () => {
      expect(getRiskIcon(level)).toBe(riskIcons[level]);
    });
  });

  describe('when "getTextColorByRiskLevel" is called', () => {
    const progressiveRiskLevels = Object.values(RiskLevel).filter(
      risk => risk !== RiskLevel.UNKNOWN && risk !== RiskLevel.RECALCULATING
    );
    describe.each(progressiveRiskLevels)(`when risk level is %s`, level => {
      it(`should return the text risk-${level} color`, () => {
        expect(getTextColorByRiskLevel(level)).toMatch(
          new RegExp(`text-risk-${level}`, "i")
        );
      });
    });

    describe.each([RiskLevel.UNKNOWN, RiskLevel.RECALCULATING])(
      `when risk level is %s`,
      level => {
        it('should return the color "text-neutral-shade-75"', () => {
          expect(getTextColorByRiskLevel(level)).toMatch(
            /text-neutral-shade-75/i
          );
        });
      }
    );
  });

  describe('when "getDefaultTextColorByRiskLevel" is called', () => {
    it('color should match "text-neutral-shade-100" when the risk is "MEDIUM"', () => {
      expect(getDefaultTextColorByRiskLevel(RiskLevel.MEDIUM)).toBe(
        "text-neutral-shade-100"
      );
    });

    it('color should match "text-neutral-shade-75" when the risk is "UNKNOWN"', () => {
      expect(getDefaultTextColorByRiskLevel(RiskLevel.UNKNOWN)).toBe(
        "text-neutral-shade-75"
      );
    });

    it('color should match "text-white" when the risk is different than "MEDIUM" or "UNKNOWN"', () => {
      expect(getDefaultTextColorByRiskLevel(RiskLevel.HIGH)).toBe("text-white");
      expect(getDefaultTextColorByRiskLevel(RiskLevel.LOW)).toBe("text-white");
    });
  });

  describe('when "getLocationRiskIconColorsByRiskLevel" is called', () => {
    const progressiveRiskLevels = Object.values(RiskLevel).filter(
      risk => risk !== RiskLevel.UNKNOWN && risk !== RiskLevel.RECALCULATING
    );
    describe.each(progressiveRiskLevels)(`when risk level is %s`, level => {
      it(`should return the background color "risk-${level.toLowerCase()}"`, () => {
        expect(getLocationRiskIconBackgroundColorByRiskLevel(level)).toMatch(
          new RegExp(`bg-risk-${level}`, "i")
        );
      });
    });

    const unknownOrRecalculatingRiskLevels = Object.values(RiskLevel).filter(
      risk => risk === RiskLevel.UNKNOWN || risk === RiskLevel.RECALCULATING
    );

    describe.each(unknownOrRecalculatingRiskLevels)(
      `when risk level is %s`,
      level => {
        it(`should return the background color "brand-gray-30"`, () => {
          expect(getLocationRiskIconBackgroundColorByRiskLevel(level)).toMatch(
            new RegExp(`bg-brand-gray-30`, "i")
          );
        });
      }
    );
  });
});
