import type { CheckboxOption } from "@/components/checkboxGroup/CheckboxGroup";
import { fireEvent, render, screen } from "@testing-library/react";
import ActivityCategory from "./ActivityCategory";

const options: CheckboxOption[] = [
  { id: "1", name: "Concrete replacement" },
  { id: "2", name: "Asphalt replacement" },
  { id: "3", name: "Soft surface" },
];

const title = "Site Restoration";
const mockOnItemChange = jest.fn();

describe(ActivityCategory.name, () => {
  it("should render a title and the count of the available options for that category", () => {
    render(
      <ActivityCategory
        title={title}
        options={options}
        onItemChange={mockOnItemChange}
      />
    );
    screen.getByText(title);
    screen.getByText(options.length);
  });

  it("should display all the options available, when clicking the accordion button", () => {
    render(
      <ActivityCategory
        title={title}
        options={options}
        onItemChange={mockOnItemChange}
      />
    );
    fireEvent.click(screen.getByRole("button"));
    options.forEach(option => {
      screen.getByText(option.name);
    });
  });
});
