import { render, screen, within } from "@testing-library/react";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { mockTenantStore } from "@/utils/dev/jest";
import LocationCard from "./LocationCard";

const locationRisk = RiskLevel.HIGH;
const locationName = "310, Main Street";
const locationSupervisor = "Montgomery Burns";
const description = "Some Project";
const projectType = "Distribution";

describe(LocationCard.name, () => {
  mockTenantStore();
  it("should render the card and display the correct risk label, according to the Risk Level passed", () => {
    const expectedOutput = `${locationRisk}`;
    render(
      <LocationCard
        risk={locationRisk}
        title={locationName}
        description={description}
        slots={[locationSupervisor]}
        identifier={projectType}
      />
    );
    screen.getByText(expectedOutput);
  });

  it("should display the project and location's names, project type and location supervisor", () => {
    render(
      <LocationCard
        risk={locationRisk}
        title={locationName}
        description={description}
        slots={[locationSupervisor]}
        identifier={projectType}
      />
    );
    screen.getByText(locationName);

    const withinList = within(screen.getByTestId("location-card"));
    withinList.getByText(projectType);
    withinList.getByText(description);
    withinList.getByText(locationSupervisor);
  });
});
