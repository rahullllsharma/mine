import {
  render,
  screen,
  fireEvent,
  waitForElementToBeRemoved,
} from "@testing-library/react";
import MapLegend from "./MapLegend";

describe(MapLegend.name, () => {
  it("should render correctly", () => {
    render(
      <MapLegend header="title" position="none">
        hello
      </MapLegend>
    );

    screen.getByText(/hello/);
  });

  it("should toggle all the items when clicked", async () => {
    render(
      <MapLegend header="title" position="none">
        hello
      </MapLegend>
    );

    fireEvent.click(screen.getByText(/title/));
    await waitForElementToBeRemoved(screen.getByText(/hello/));

    fireEvent.click(screen.getByText(/title/));
    expect(await screen.findByText(/hello/)).toBeVisible();
  });
});
