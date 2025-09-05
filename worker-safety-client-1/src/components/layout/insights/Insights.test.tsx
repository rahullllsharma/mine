import { render, screen } from "@testing-library/react";
import { mockTenantStore } from "@/utils/dev/jest";
import Insights from "./Insights";

const mockTabChange = jest.fn();

describe(Insights.name, () => {
  mockTenantStore();
  describe("when it renders", () => {
    it("should match the snapshot", () => {
      const { asFragment } = render(
        <Insights emptyChartsTitle="" onTabChange={mockTabChange} />
      );
      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe("when contains a filter element", () => {
    it("should render the filter element", () => {
      render(
        <Insights
          filters={<div>Lorem ipsum</div>}
          emptyChartsTitle=""
          onTabChange={mockTabChange}
        />
      );
      screen.getByText(/lorem ipsum/i);
    });
  });

  describe("when contains a chart element", () => {
    it("should render the chart element", () => {
      render(
        <Insights
          charts={[<div key={1}>Lorem ipsum</div>]}
          emptyChartsTitle=""
          onTabChange={mockTabChange}
        />
      );
      screen.getByText(/lorem ipsum/i);
    });
  });

  describe("when no charts are passed", () => {
    it("should render empty content message", () => {
      render(
        <Insights
          filters={<div>Lorem ipsum</div>}
          emptyChartsTitle="There are no charts available"
          onTabChange={mockTabChange}
        />
      );
      screen.getByText(/there are no charts available/i);
    });
  });
});
