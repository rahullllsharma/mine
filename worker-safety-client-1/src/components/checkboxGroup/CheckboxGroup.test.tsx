import type { InputSelectOption } from "../shared/inputSelect/InputSelect";
import { fireEvent, render, screen } from "@testing-library/react";
import CheckboxGroup from "./CheckboxGroup";

const options: InputSelectOption[] = [
  { id: "m_1", name: "In progress" },
  { id: "m_2", name: "Active" },
  { id: "m_3", name: "Complete" },
];

const mockOnChange = jest.fn();

describe(CheckboxGroup.name, () => {
  beforeEach(() => {
    render(<CheckboxGroup options={options} onChange={mockOnChange} />);
  });

  describe("when it renders", () => {
    it("should have the options displayed", () => {
      screen.getByText(/in progress/i);
      screen.getByText(/active/i);
      screen.getByText(/complete/i);
    });
  });

  describe("when an option is selected", () => {
    it('should call "onSelect" with the checked options', () => {
      const checkbox = screen.getByText(/active/i);
      fireEvent.click(checkbox);
      expect(mockOnChange).toHaveBeenCalledWith([options[1]]);
    });
  });

  describe("when multiple options are selected", () => {
    it('should call "onSelect" with the checked options', () => {
      fireEvent.click(screen.getByText(/in progress/i));
      fireEvent.click(screen.getByText(/active/i));
      fireEvent.click(screen.getByText(/complete/i));

      expect(mockOnChange).toHaveBeenCalledWith([...options]);
    });
  });
});
