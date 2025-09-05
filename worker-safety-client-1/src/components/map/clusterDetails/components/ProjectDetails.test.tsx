import { render, screen } from "@testing-library/react";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { mockTenantStore } from "@/utils/dev/jest";
import ProjectDetails from "./ProjectDetails";

describe(ProjectDetails.name, () => {
  mockTenantStore();
  it("should render correctly", () => {
    const { asFragment } = render(
      <ProjectDetails
        riskLevel={RiskLevel.LOW}
        projectName="Project ACME"
        supervisorName="John Doe"
      />
    );

    expect(asFragment()).toMatchSnapshot();

    screen.getByRole("heading", { level: 5, name: /project acme/i });
    screen.getByText(/john doe/i);
  });
});
