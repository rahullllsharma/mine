import { render, screen, fireEvent } from "@testing-library/react";
import Switch from "./Switch";

describe("Switch", () => {
  const mockOnToggle = jest.fn();

  afterEach(() => {
    mockOnToggle.mockClear();
  });

  it("should render", () => {
    render(<Switch onToggle={mockOnToggle} />);
    const buttonElement = screen.getByRole("switch");
    expect(buttonElement).toBeInTheDocument();
  });

  it('should have an initial state value defined by "stateOverride" property', () => {
    render(<Switch stateOverride={true} onToggle={mockOnToggle} />);
    const buttonElement = screen.getByRole("switch");
    expect(buttonElement).toBeChecked();
  });
  it("should switch to checked state when clicked if current state is unchecked", () => {
    render(<Switch stateOverride={false} onToggle={mockOnToggle} />);
    fireEvent.click(screen.getByRole("switch"));

    const buttonElement = screen.getByRole("switch");
    expect(buttonElement).toBeChecked();
  });
  it("should switch to unchecked state when clicked if current state is checked", () => {
    render(<Switch stateOverride={true} onToggle={mockOnToggle} />);
    fireEvent.click(screen.getByRole("switch"));

    const buttonElement = screen.getByRole("switch");
    expect(buttonElement).not.toBeChecked();
  });

  describe("when is disabled", () => {
    beforeEach(() => {
      render(
        <Switch
          stateOverride={false}
          isDisabled={true}
          onToggle={mockOnToggle}
        />
      );
    });

    it("should render the switch button disabled", () => {
      const buttonElement = screen.getByRole("switch");
      expect(buttonElement).toBeDisabled();
    });

    it('should maintain the same state if the "isDisabled" property is defined as "true"', () => {
      fireEvent.click(screen.getByRole("switch"));

      const buttonElement = screen.getByRole("switch");
      expect(buttonElement).not.toBeChecked();
    });

    it("should not call 'onToggle' function", () => {
      fireEvent.click(screen.getByRole("switch"));
      expect(mockOnToggle).not.toHaveBeenCalled();
    });
  });
});
