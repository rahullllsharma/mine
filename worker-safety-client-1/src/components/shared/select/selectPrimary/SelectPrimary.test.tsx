import type { SelectOptionTooltip } from "../Select";
import type { SelectPrimaryOption } from "./SelectPrimary";
import { fireEvent, render, screen } from "@testing-library/react";
import SelectPrimary from "./SelectPrimary";

const DUMMY_LOCATIONS: SelectPrimaryOption[] = [
  { id: 1, name: "Location 1" },
  { id: 2, name: "Location 2" },
  { id: 3, name: "Location 3" },
  { id: 4, name: "Location 4" },
];

const itemSelectHandler = jest.fn();

describe(SelectPrimary.name, () => {
  it("renders currently", () => {
    const { asFragment } = render(
      <SelectPrimary options={DUMMY_LOCATIONS} onSelect={itemSelectHandler} />
    );

    expect(asFragment()).toMatchSnapshot();

    const buttonElement = screen.getByRole("button");
    expect(buttonElement).toBeInTheDocument();
  });

  it("should render the list items correctly", () => {
    const { asFragment } = render(
      <SelectPrimary options={DUMMY_LOCATIONS} onSelect={itemSelectHandler} />
    );

    fireEvent.click(screen.getByRole("button"));
    expect(asFragment()).toMatchSnapshot();
  });

  describe("when an option is disabled", () => {
    it("should include the disabled attribute", () => {
      render(
        <SelectPrimary
          options={DUMMY_LOCATIONS.map(option =>
            option.id === 3 ? { ...option, isDisabled: true } : option
          )}
          onSelect={itemSelectHandler}
        />
      );

      fireEvent.click(screen.getByRole("button"));
      const disabledOption = screen.getByRole("option", {
        name: DUMMY_LOCATIONS[2].name,
      });
      expect(disabledOption).toHaveAttribute("aria-disabled");
    });
  });

  describe("when an option has a tooltio", () => {
    it("should include an icon that will show a tooltip", () => {
      const tooltip: SelectOptionTooltip = {
        icon: "info_circle_outline",
        text: "Lorem ipsum",
      };
      const { asFragment } = render(
        <SelectPrimary
          options={DUMMY_LOCATIONS.map(option =>
            option.id === 3
              ? {
                  ...option,
                  tooltip,
                }
              : option
          )}
          onSelect={itemSelectHandler}
        />
      );
      fireEvent.click(screen.getByRole("button"));
      expect(asFragment()).toMatchSnapshot();
    });
  });
});
