import { render, screen, within } from "@testing-library/react";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { mockTenantStore } from "@/utils/dev/jest";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import ClusterDetails from "./ClusterDetails";

describe(ClusterDetails.name, () => {
  mockTenantStore();
  it("should render correctly", () => {
    const { asFragment } = render(
      <ClusterDetails
        totalTitle="Cluster title"
        totals={{ HIGH: 1, MEDIUM: 1, LOW: 1, UNKNOWN: 1 }}
      />
    );

    expect(asFragment()).toMatchSnapshot();
  });

  it("should render the risk, project and supervisor details when passed", () => {
    const { asFragment } = render(
      <ClusterDetails
        riskLevel={RiskLevel.LOW}
        projectName="Project ACME"
        supervisorName="John Doe"
        totalTitle="Cluster title"
        totals={{ HIGH: 1, MEDIUM: 1, LOW: 1 }}
      />
    );

    expect(asFragment()).toMatchSnapshot();

    screen.getByRole("heading", { level: 5, name: /project acme/gi });
    screen.getByText(
      `${
        useTenantStore.getState().getAllEntities().workPackage.attributes
          .primaryAssignedPerson.label
      }: John Doe`
    );
  });

  it.each`
    high         | medium       | low          | unknown
    ${4}         | ${3}         | ${2}         | ${1}
    ${3}         | ${2}         | ${1}         | ${undefined}
    ${2}         | ${1}         | ${undefined} | ${undefined}
    ${1}         | ${undefined} | ${undefined} | ${undefined}
    ${undefined} | ${undefined} | ${undefined} | ${undefined}
  `(
    "should render totals per element (high: $high, med: $medium, low: $low, unknown: $unknown)",
    expected => {
      const totalsArr: [string, string | undefined][] =
        Object.entries(expected);
      const totals = totalsArr.reduce(
        (acc, [key, value]) => ({
          ...acc,
          [key.toUpperCase()]: value,
        }),
        {}
      );

      render(<ClusterDetails totalTitle="title" totals={totals} />);

      totalsArr.forEach(([key, value]) => {
        const testId = `cluster-detail-risk-badge-${key}`;
        if (value) {
          expect(screen.getByTestId(testId)).toBeInTheDocument();

          // Now test that the element has the correct value
          const badge = within(screen.getByTestId(testId));
          expect(badge.getByText(value, { exact: false })).toBeInTheDocument();
        } else {
          expect(screen.queryByTestId(testId)).not.toBeInTheDocument();
        }
      });
    }
  );
});
