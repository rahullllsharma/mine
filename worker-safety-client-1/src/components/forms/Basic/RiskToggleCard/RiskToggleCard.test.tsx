import type { RiskToggleCardProps } from "./RiskToggleCard";
import { fireEvent, render, screen } from "@testing-library/react";

import { RiskToggleCard } from "./RiskToggleCard";

describe(RiskToggleCard.name, () => {
  let props: RiskToggleCardProps;

  beforeEach(() => {
    props = {
      onClick: jest.fn(),
      checked: false,
      risk: "ArcFlash",
    };
  });

  it("renders correctly", () => {
    const { asFragment } = render(<RiskToggleCard {...props} />);

    expect(asFragment()).toMatchSnapshot();
  });

  describe("user actions", () => {
    it("user clicked on the toggle triggers correct behavior", () => {
      render(<RiskToggleCard {...props} />);

      const toggle = screen.getByRole("checkbox");
      fireEvent.click(toggle);

      expect(props.onClick).toHaveBeenCalledTimes(1);
    });
  });
});
