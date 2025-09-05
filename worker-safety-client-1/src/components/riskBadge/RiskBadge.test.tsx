import { screen, render } from "@testing-library/react";
import RiskBadge from "./RiskBadge";
import { RiskLevel } from "./RiskLevel";

describe(RiskBadge.name, () => {
  describe.each(Object.values(RiskLevel))(`when risk level is %s`, level => {
    it(`should contain className corresponding to '${level}'`, () => {
      render(<RiskBadge risk={level} label="some label" />);
      const labelElement: HTMLElement = screen.getByRole("note");
      expect(labelElement.classList.value).toMatch(
        new RegExp(`bg-risk-${level}`, "i")
      );
    });
  });

  describe('when risk level is "Recalculating"', () => {
    it("should render a badge with animation", () => {
      render(<RiskBadge risk={RiskLevel.RECALCULATING} label="some label" />);

      screen.getByText(/some label/i);
      screen.getByRole("note");
      //screen.getByRole("status"); // commented tue to WS-1276
    });
  });
});
