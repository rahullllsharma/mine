import { render, screen } from "@testing-library/react";
import { mockTenantStore } from "@/utils/dev/jest";
import LocationList from "./LocationList";
import { mockLocations } from "./mock/mockLocations";

describe(LocationList.name, () => {
  mockTenantStore();
  it("should display as many cards as the locations passed to the component", () => {
    render(<LocationList locations={mockLocations} />);
    const cards = screen.getAllByTestId("location-card");
    expect(cards).toHaveLength(mockLocations.length);
  });

  it("should't display any cards when an empty array is passed to the component", () => {
    render(<LocationList locations={[]} />);
    const cards = screen.queryAllByTestId("location-card");
    expect(cards).toHaveLength(0);
  });
});
