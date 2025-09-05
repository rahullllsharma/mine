import { render, screen } from "@testing-library/react";
import EmptyChart from "./EmptyChart";

describe(EmptyChart.name, () => {
  describe("when it renders", () => {
    it("should contain a title", () => {
      render(
        <EmptyChart
          title="This is the title"
          description="This is the description"
        />
      );
      screen.getByText(/this is the title/i);
    });

    it("should contain a description", () => {
      render(
        <EmptyChart
          title="This is the title"
          description="This is a description"
        />
      );
      screen.getByText(/this is a description/i);
    });
  });
});
