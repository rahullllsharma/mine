import type { InputSelectOption } from "@/components/shared/inputSelect/InputSelect";
import { render, screen } from "@testing-library/react";
import MultiOptionWrapper from "./MultiOptionWrapper";

const options: InputSelectOption[] = [
  { id: "m_1", name: "In progress" },
  { id: "m_2", name: "Active" },
  { id: "m_3", name: "Complete" },
  { id: "m_4", name: "Inactive" },
];

const mockOnSelect = jest.fn();

describe(MultiOptionWrapper.name, () => {
  describe('when it renders with type "multiSelect"', () => {
    it('should render a "MultiSelect" component', () => {
      render(
        <MultiOptionWrapper
          options={options}
          onSelect={mockOnSelect}
          type="multiSelect"
        />
      );
      screen.getByRole("button", { name: /select.../i });
    });
  });

  describe('when it renders with type "checkbox"', () => {
    it('should render a "CheckboxGroup" component', () => {
      render(
        <MultiOptionWrapper
          options={options}
          onSelect={mockOnSelect}
          type="checkbox"
        />
      );
      const checkboxes = screen.getAllByRole("checkbox");
      expect(checkboxes.length).toBe(options.length);
    });
  });

  describe("when it renders without type", () => {
    it('should render a "CheckboxGroup" if the options are 4 or less', () => {
      render(<MultiOptionWrapper options={options} onSelect={mockOnSelect} />);
      const checkboxes = screen.getAllByRole("checkbox");
      expect(checkboxes.length).toBe(options.length);
    });

    it('should render a "MultiSelect" if the options are more than 4', () => {
      const testOptions = [...options, { id: "m_5", name: "pending" }];
      render(
        <MultiOptionWrapper options={testOptions} onSelect={mockOnSelect} />
      );
      screen.getByRole("button", { name: /select.../i });
    });
  });
});
