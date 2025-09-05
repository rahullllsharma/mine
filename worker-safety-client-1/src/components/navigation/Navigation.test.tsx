import type { NavigationOption } from "./Navigation";
import { render, screen, fireEvent } from "@testing-library/react";
import Navigation from "./Navigation";

const options: NavigationOption[] = [
  {
    id: 0,
    name: "Details",
    icon: "settings_filled",
  },
  {
    id: 1,
    name: "Locations",
    icon: "location",
  },
  {
    id: 2,
    name: "History",
    icon: "history",
  },
];

const mockOnChange = jest.fn();

describe(Navigation.name, () => {
  describe("when it renders", () => {
    it("should match the snapshot", () => {
      const { asFragment } = render(
        <Navigation
          options={options}
          onChange={mockOnChange}
          selectedIndex={0}
        />
      );
      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe('when the "onChange" callback is called from the select component', () => {
    it("should return the index of the option", () => {
      render(
        <Navigation
          options={options}
          onChange={mockOnChange}
          selectedIndex={0}
        />
      );
      fireEvent.click(screen.getByRole("button")); //the button is the trigger for the select
      fireEvent.click(screen.getByRole("option", { name: options[1].name }));
      expect(mockOnChange).toBeCalledWith(1);
    });
  });
});
