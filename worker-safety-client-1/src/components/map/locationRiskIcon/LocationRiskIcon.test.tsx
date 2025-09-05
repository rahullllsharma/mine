import { render, screen } from "@testing-library/react";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import LocationRiskIcon from "./LocationRiskIcon";

describe(LocationRiskIcon.name, () => {
  it("should render correctly", () => {
    const { asFragment } = render(
      <LocationRiskIcon riskLevel={RiskLevel.HIGH} label="title" />
    );

    expect(asFragment()).toMatchSnapshot();
  });

  it("should display the title correctly", () => {
    render(<LocationRiskIcon riskLevel={RiskLevel.HIGH} label="title" />);
    screen.getByRole("status", {
      name: /title/i,
    });
  });
});
