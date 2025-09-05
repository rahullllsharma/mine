import { render, screen } from "@testing-library/react";
import Control from "./ControlCard";

describe("ControlCard", () => {
  it("should render a label", () => {
    render(<Control label="Lorem ipsum" />);
    const labelElement = screen.getByText("Lorem ipsum");
    expect(labelElement).toBeInTheDocument();
  });

  it("should render a control with an action", () => {
    render(
      <Control label="Lorem ipsum">
        <button />
      </Control>
    );
    const button = screen.getByRole("button");
    expect(button).toBeInTheDocument();
  });
});
