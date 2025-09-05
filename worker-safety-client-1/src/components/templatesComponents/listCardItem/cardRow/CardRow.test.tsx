import { render, screen } from "@testing-library/react";
import CardRow from "./CardRow";

describe(CardRow.name, () => {
  describe("when it renders", () => {
    it("should render with a label", () => {
      render(<CardRow label="Region" />);
      screen.getByText("Region");
    });

    it("should render with children", () => {
      render(
        <CardRow label="Region">
          <div>Children Text</div>
        </CardRow>
      );
      screen.getByText("Children Text");
    });
  });
});
