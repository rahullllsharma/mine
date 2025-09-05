import type { NavigationOption } from "../navigation/Navigation";
import { render, screen, fireEvent } from "@testing-library/react";
import Sidebar from "./Sidebar";

const TAB_OPTIONS: NavigationOption[] = [
  {
    id: 0,
    name: "Project details",
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

describe(Sidebar.name, () => {
  it("should render correctly", () => {
    const { asFragment } = render(
      <Sidebar
        options={TAB_OPTIONS}
        selectedIndex={0}
        onChange={mockOnChange}
      />
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("should display tabs with the correct value for each valid option", () => {
    render(
      <Sidebar
        options={TAB_OPTIONS}
        selectedIndex={0}
        onChange={mockOnChange}
      />
    );
    TAB_OPTIONS.forEach(option =>
      screen.getByRole("tab", { name: option.name })
    );
  });

  it('should render with option selected that matches the "selectedIndex" prop', () => {
    render(
      <Sidebar
        options={TAB_OPTIONS}
        selectedIndex={1}
        onChange={mockOnChange}
      />
    );
    const selectedElement = screen.getByRole("tab", {
      name: TAB_OPTIONS[1].name,
    });
    expect(selectedElement).toHaveAttribute("aria-selected", "true");
  });

  it('should render with the first option selected, if the "selectedIndex" is bigger than the number of options', () => {
    render(
      <Sidebar
        options={TAB_OPTIONS}
        selectedIndex={5}
        onChange={mockOnChange}
      />
    );
    const selectedElement = screen.getByRole("tab", {
      name: TAB_OPTIONS[0].name,
    });
    expect(selectedElement).toHaveAttribute("aria-selected", "true");
  });

  it('should call the "onChange" callback when an item is selected', () => {
    render(
      <Sidebar
        options={TAB_OPTIONS}
        selectedIndex={0}
        onChange={mockOnChange}
      />
    );
    const selectedElement = screen.getByRole("tab", {
      name: TAB_OPTIONS[1].name,
    });
    fireEvent.click(selectedElement);
    expect(mockOnChange).toBeCalledWith(1);
  });
});
