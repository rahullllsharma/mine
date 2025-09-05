import { render, screen } from "@testing-library/react";
import { mockTenantStore } from "@/utils/dev/jest";
import ChartCard from "./ChartCard";

describe(ChartCard.name, () => {
  mockTenantStore();
  describe("when it renders", () => {
    it("should match the snapshot", () => {
      const { asFragment } = render(
        <ChartCard title="lorem ipsum" type="hazard" />
      );
      expect(asFragment()).toMatchSnapshot();
    });

    it('should have a text element based on the "title" prop', () => {
      render(<ChartCard title="lorem ipsum" type="hazard" />);
      screen.getByText(/lorem ipsum/i);
    });
  });

  describe('when a react node is passed in the "charts" prop', () => {
    it("should render the node", () => {
      render(
        <ChartCard
          title="lorem ipsum"
          type="hazard"
          chart={<div>This is a chart</div>}
        />
      );
      screen.getByText(/this is a chart/i);
    });
  });
});
