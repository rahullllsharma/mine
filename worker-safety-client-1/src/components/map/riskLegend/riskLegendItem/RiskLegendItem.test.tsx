import { render, screen } from "@testing-library/react";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import RiskLegendItem from "./RiskLegendItem";

describe(RiskLegendItem.name, () => {
  it("should render correctly", () => {
    render(<RiskLegendItem riskLevel={RiskLevel.LOW} legend="Low Risk" />);
    screen.getByRole("status", {
      name: /low risk/i,
    });

    screen.getByText(/low risk/i);
  });
});
