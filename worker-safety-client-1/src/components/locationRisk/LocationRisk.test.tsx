import { render, screen } from "@testing-library/react";
import { mockTenantStore } from "@/utils/dev/jest";
import { RiskLevel } from "../riskBadge/RiskLevel";
import LocationRisk from "./LocationRisk";

describe(LocationRisk.name, () => {
  mockTenantStore();
  describe("when it renders", () => {
    it("should match the snapshot", () => {
      const { asFragment } = render(<LocationRisk risk={RiskLevel.MEDIUM} />);
      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe("when it renders with a supervisor risk warning", () => {
    it('should display an "at risk" supervisor row', () => {
      const { asFragment } = render(
        <LocationRisk risk={RiskLevel.MEDIUM} supervisorRisk />
      );
      screen.getByText(/at risk/i);
      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe("when it renders with a contractor risk warning", () => {
    it('should display an "at risk" contractor row', () => {
      const { asFragment } = render(
        <LocationRisk risk={RiskLevel.MEDIUM} contractorRisk />
      );
      screen.getByText(/at risk/i);
      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe("when it renders with a crew risk warning", () => {
    it('should display an "at risk" crew row', () => {
      const { asFragment } = render(
        <LocationRisk risk={RiskLevel.MEDIUM} crewRisk />
      );
      screen.getByText(/at risk/i);
      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe("when it renders with both supervisor and contractor risk warnings", () => {
    it('should display two "at risk" rows', () => {
      const { asFragment } = render(
        <LocationRisk risk={RiskLevel.MEDIUM} supervisorRisk contractorRisk />
      );
      expect(asFragment()).toMatchSnapshot();
    });
  });
});
