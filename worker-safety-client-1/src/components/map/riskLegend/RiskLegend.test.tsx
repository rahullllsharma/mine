import {
  render,
  screen,
  fireEvent,
  waitForElementToBeRemoved,
} from "@testing-library/react";
import RiskLegend from "./RiskLegend";

describe(RiskLegend.name, () => {
  it("should render correctly", () => {
    render(<RiskLegend label="title" />);

    screen.getByText(/title/);
    expect(
      screen.getByRole("status", {
        name: /high/i,
      })
    ).toBeInTheDocument();
  });

  it("should toggle all the items when clicked", async () => {
    render(<RiskLegend label="title" />);

    fireEvent.click(screen.getByText(/title/));
    await waitForElementToBeRemoved(
      screen.getByRole("status", {
        name: /high/i,
      })
    );

    fireEvent.click(screen.getByText(/title/));
    expect(
      await screen.findByRole("status", {
        name: /high/i,
      })
    ).toBeVisible();
  });
});
