import { fireEvent, render, screen } from "@testing-library/react";
import Tabs from "./Tabs";

const options = ["Active", "Pending", "Completed"];
const mockOnSelect = jest.fn();

describe(Tabs.name, () => {
  it("should render with the first item selected", () => {
    render(<Tabs options={options} onSelect={mockOnSelect} />);
    const selectedElement = screen.getByRole("tab", { name: options[0] });
    expect(selectedElement.getAttribute("aria-selected")).toBeTruthy();
  });

  it('should render with a different option selected based on the "defaultIndex" prop', () => {
    render(<Tabs options={options} defaultIndex={1} onSelect={mockOnSelect} />);
    const selectedElement = screen.getByRole("tab", { name: options[1] });
    expect(selectedElement.getAttribute("aria-selected")).toBeTruthy();
  });

  it("should switch the selected element when clicked", () => {
    render(<Tabs options={options} onSelect={mockOnSelect} />);
    const selectedElement = screen.getByRole("tab", { name: options[1] });
    fireEvent.click(selectedElement);
    expect(selectedElement.getAttribute("aria-selected")).toBeTruthy();
  });

  it('should call the "onSelect" callback when an item is selected', () => {
    render(<Tabs options={options} onSelect={mockOnSelect} />);
    const selectedElement = screen.getByRole("tab", { name: options[1] });
    fireEvent.click(selectedElement);
    expect(mockOnSelect).toBeCalledWith(1, options[1]);
  });
});
