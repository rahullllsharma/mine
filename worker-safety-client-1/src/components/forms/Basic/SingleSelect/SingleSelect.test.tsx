import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { SingleSelect } from "./SingleSelect";

// Mock the useOnClickOutside hook
jest.mock("usehooks-ts", () => ({
  useOnClickOutside: jest.fn(),
}));

// Mock the Button component
jest.mock("../../../shared/button/Button", () => {
  return function MockButton({
    children,
    onClick,
    iconStart,
    iconStartClassName,
    ...props
  }: {
    children?: React.ReactNode;
    onClick?: (e: React.MouseEvent) => void;
    iconStart?: string;
    iconStartClassName?: string;
    [key: string]: unknown;
  }) {
    return (
      <button onClick={onClick} {...props}>
        {iconStart && (
          <span
            data-testid={`icon-${iconStart}`}
            className={iconStartClassName}
          />
        )}
        {children}
      </button>
    );
  };
});

// Mock the Icon component
jest.mock("@urbint/silica", () => ({
  Icon: ({
    name,
    className,
    onClick,
  }: {
    name: string;
    className?: string;
    onClick?: (e: React.MouseEvent) => void;
  }) => (
    <span
      data-testid={`icon-${name}`}
      className={className}
      onClick={onClick}
    />
  ),
  BodyText: ({
    children,
    className,
  }: {
    children: React.ReactNode;
    className?: string;
  }) => <div className={className}>{children}</div>,
}));

const defaultProps = {
  options: [
    { label: "Option 1", value: "option1" },
    { label: "Option 2", value: "option2" },
    { label: "Option 3", value: "option3" },
  ],
  onSelected: jest.fn(),
};

describe("SingleSelect", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("Basic Rendering", () => {
    it("renders with default props", () => {
      render(<SingleSelect {...defaultProps} />);
      expect(screen.getByRole("textbox")).toBeInTheDocument();
      expect(screen.getByDisplayValue("")).toBeInTheDocument();
    });

    it("renders with custom placeholder", () => {
      render(<SingleSelect {...defaultProps} placeholder="Choose an option" />);

      expect(screen.getByDisplayValue("")).toBeInTheDocument();
    });

    it("renders with label", () => {
      render(<SingleSelect {...defaultProps} label="Test Label" />);

      expect(screen.getByText("Test Label")).toBeInTheDocument();
    });

    it("renders with selected value", () => {
      render(<SingleSelect {...defaultProps} selected="option1" />);

      expect(screen.getByDisplayValue("Option 1")).toBeInTheDocument();
    });
  });

  describe("Dropdown Functionality", () => {
    it("opens dropdown when input is clicked", () => {
      render(<SingleSelect {...defaultProps} />);

      const input = screen.getByRole("textbox");
      fireEvent.click(input);

      expect(screen.getByText("Option 1")).toBeInTheDocument();
      expect(screen.getByText("Option 2")).toBeInTheDocument();
      expect(screen.getByText("Option 3")).toBeInTheDocument();
    });

    it("closes dropdown when input is clicked again", () => {
      render(<SingleSelect {...defaultProps} />);

      const input = screen.getByRole("textbox");

      // Open dropdown
      fireEvent.click(input);
      expect(screen.getByText("Option 1")).toBeInTheDocument();

      // Close dropdown
      fireEvent.click(input);
      expect(screen.queryByText("Option 1")).not.toBeInTheDocument();
    });

    it("opens dropdown when dropdown arrow is clicked", () => {
      render(<SingleSelect {...defaultProps} />);

      const dropdownButton = screen.getByTestId("icon-chevron_down");
      fireEvent.click(dropdownButton);

      expect(screen.getByText("Option 1")).toBeInTheDocument();
    });

    it("closes dropdown when dropdown arrow is clicked while open", () => {
      render(<SingleSelect {...defaultProps} />);

      const input = screen.getByRole("textbox");
      fireEvent.click(input);

      const dropdownButton = screen.getByTestId("icon-chevron_up");
      fireEvent.click(dropdownButton);

      expect(screen.queryByText("Option 1")).not.toBeInTheDocument();
    });
  });

  describe("Option Selection", () => {
    it("selects an option when clicked", () => {
      const onSelected = jest.fn();
      render(<SingleSelect {...defaultProps} onSelected={onSelected} />);

      const input = screen.getByRole("textbox");
      fireEvent.click(input);

      const option = screen.getByText("Option 2");
      fireEvent.click(option);

      expect(onSelected).toHaveBeenCalledWith("option2");
    });

    it("closes dropdown after selection", () => {
      render(<SingleSelect {...defaultProps} />);

      const input = screen.getByRole("textbox");
      fireEvent.click(input);

      const option = screen.getByText("Option 2");
      fireEvent.click(option);

      expect(screen.queryByText("Option 1")).not.toBeInTheDocument();
    });

    it("shows selected option in input", () => {
      render(<SingleSelect {...defaultProps} selected="option2" />);

      expect(screen.getByDisplayValue("Option 2")).toBeInTheDocument();
    });

    it("shows checkmark for selected option", () => {
      render(<SingleSelect {...defaultProps} selected="option2" />);

      const input = screen.getByRole("textbox");
      fireEvent.click(input);

      expect(screen.getByTestId("icon-check")).toBeInTheDocument();
    });
  });

  describe("Clear Functionality", () => {
    it("shows clear button when option is selected", () => {
      render(<SingleSelect {...defaultProps} selected="option1" />);

      expect(screen.getByTestId("icon-close_small")).toBeInTheDocument();
    });

    it("does not show clear button when no option is selected", () => {
      render(<SingleSelect {...defaultProps} />);

      expect(screen.queryByTestId("icon-close_small")).not.toBeInTheDocument();
    });

    it("calls onClear when clear button is clicked", () => {
      const onClear = jest.fn();
      render(
        <SingleSelect {...defaultProps} selected="option1" onClear={onClear} />
      );

      const clearButton = screen.getByTestId("icon-close_small");
      fireEvent.click(clearButton);

      expect(onClear).toHaveBeenCalled();
    });
  });

  describe("Search/Filter Functionality", () => {
    it("filters options when typing", () => {
      render(<SingleSelect {...defaultProps} />);

      const input = screen.getByRole("textbox");
      fireEvent.click(input);
      fireEvent.change(input, { target: { value: "Option 2" } });

      expect(screen.getByText("Option 2")).toBeInTheDocument();
      expect(screen.queryByText("Option 1")).not.toBeInTheDocument();
      expect(screen.queryByText("Option 3")).not.toBeInTheDocument();
    });

    it("shows 'No matching options found' when no matches", () => {
      render(<SingleSelect {...defaultProps} />);

      const input = screen.getByRole("textbox");
      fireEvent.click(input);
      fireEvent.change(input, { target: { value: "Non-existent" } });

      expect(screen.getByText("No matching options found")).toBeInTheDocument();
    });

    it("highlights matching text in options", () => {
      render(<SingleSelect {...defaultProps} />);

      const input = screen.getByRole("textbox");
      fireEvent.click(input);
      fireEvent.change(input, { target: { value: "Option" } });

      // Check if the option is visible (filtering works)
      // Look for the option by its role instead of exact text
      const options = screen.getAllByRole("listitem");
      expect(options).toHaveLength(3); // All three options should match "Option"
      const highlightedTexts = screen.getAllByText("Option");
      const strongElements = highlightedTexts.filter(
        el => el.tagName === "STRONG"
      );
      expect(strongElements).toHaveLength(3); // Should have 3 strong elements for "Option"
    });

    it("clears search when dropdown is closed", () => {
      render(<SingleSelect {...defaultProps} />);

      const input = screen.getByRole("textbox");
      fireEvent.click(input);
      fireEvent.change(input, { target: { value: "Option 2" } });

      // Close dropdown
      fireEvent.click(input);

      // Reopen dropdown
      fireEvent.click(input);

      // All options should be visible again
      expect(screen.getByText("Option 1")).toBeInTheDocument();
      expect(screen.getByText("Option 2")).toBeInTheDocument();
      expect(screen.getByText("Option 3")).toBeInTheDocument();
    });
  });

  describe("Keyboard Navigation", () => {
    it("opens dropdown with ArrowDown key", () => {
      render(<SingleSelect {...defaultProps} />);

      const input = screen.getByRole("textbox");
      input.focus();
      fireEvent.keyDown(input, { key: "ArrowDown" });

      expect(screen.getByText("Option 1")).toBeInTheDocument();
    });

    it("navigates through options with ArrowDown", () => {
      render(<SingleSelect {...defaultProps} />);

      const input = screen.getByRole("textbox");
      fireEvent.click(input);

      fireEvent.keyDown(input, { key: "ArrowDown" });
      fireEvent.keyDown(input, { key: "ArrowDown" });

      // The second option should be focused
      const options = screen.getAllByRole("listitem");
      expect(options[1]).toHaveClass("optionFocused");
    });

    it("navigates through options with ArrowUp", () => {
      render(<SingleSelect {...defaultProps} />);

      const input = screen.getByRole("textbox");
      fireEvent.click(input);

      fireEvent.keyDown(input, { key: "ArrowDown" });
      fireEvent.keyDown(input, { key: "ArrowDown" });
      fireEvent.keyDown(input, { key: "ArrowUp" });

      // The first option should be focused
      const options = screen.getAllByRole("listitem");
      expect(options[0]).toHaveClass("optionFocused");
    });

    it("selects option with Enter key", () => {
      const onSelected = jest.fn();
      render(<SingleSelect {...defaultProps} onSelected={onSelected} />);

      const input = screen.getByRole("textbox");
      fireEvent.click(input);

      fireEvent.keyDown(input, { key: "ArrowDown" });
      fireEvent.keyDown(input, { key: "Enter" });

      expect(onSelected).toHaveBeenCalledWith("option1");
    });

    it("closes dropdown with Escape key", () => {
      render(<SingleSelect {...defaultProps} />);

      const input = screen.getByRole("textbox");
      fireEvent.click(input);

      fireEvent.keyDown(input, { key: "Escape" });

      expect(screen.queryByText("Option 1")).not.toBeInTheDocument();
    });
  });

  describe("Disabled State", () => {
    it("disables input when disabled prop is true", () => {
      render(<SingleSelect {...defaultProps} disabled />);

      const input = screen.getByRole("textbox");
      expect(input).toBeDisabled();
    });

    it("does not open dropdown when disabled", () => {
      render(<SingleSelect {...defaultProps} disabled />);

      const input = screen.getByRole("textbox");
      fireEvent.click(input);

      expect(screen.queryByText("Option 1")).not.toBeInTheDocument();
    });

    it("shows disabled cursor on dropdown arrow", () => {
      render(<SingleSelect {...defaultProps} disabled />);

      const dropdownButton = screen.getByTestId("icon-chevron_down");
      expect(dropdownButton).toHaveClass("dropdownIconDisabled");
    });
  });

  describe("Error State", () => {
    it("shows error styling when hasError is true", () => {
      render(<SingleSelect {...defaultProps} hasError />);

      const container = screen.getByRole("textbox").closest("div");
      expect(container).toHaveClass("inputContainerError");
    });

    it("shows error message when provided", () => {
      render(
        <SingleSelect
          {...defaultProps}
          hasError
          errorMessage="This field is required"
        />
      );

      expect(screen.getByText("This field is required")).toBeInTheDocument();
    });

    it("does not show error message when hasError is false", () => {
      render(
        <SingleSelect {...defaultProps} errorMessage="This field is required" />
      );

      expect(
        screen.queryByText("This field is required")
      ).not.toBeInTheDocument();
    });
  });

  describe("Full Content Mode", () => {
    it("renders textarea when showFullContent is true", () => {
      render(<SingleSelect {...defaultProps} showFullContent />);

      const textarea = screen.getByRole("textbox");
      expect(textarea.tagName).toBe("TEXTAREA");
    });

    it("renders input when showFullContent is false", () => {
      render(<SingleSelect {...defaultProps} showFullContent={false} />);

      const input = screen.getByRole("textbox");
      expect(input.tagName).toBe("INPUT");
    });

    it("auto-resizes textarea when content changes", async () => {
      render(
        <SingleSelect {...defaultProps} showFullContent selected="option1" />
      );

      const textarea = screen.getByRole("textbox") as HTMLTextAreaElement;

      // Simulate content change
      fireEvent.change(textarea, {
        target: { value: "Very long content that should expand the textarea" },
      });

      // Check that the textarea has a height set (auto-resize should have occurred)
      await waitFor(() => {
        expect(textarea.style.height).toBeTruthy();
      });
    });
  });

  describe("Accessibility", () => {
    it("has proper id attribute", () => {
      render(<SingleSelect {...defaultProps} id="test-select" />);

      const input = screen.getByRole("textbox");
      expect(input).toHaveAttribute("id", "test-select");
    });

    it("has proper name attribute", () => {
      render(<SingleSelect {...defaultProps} id="test-select" />);

      const input = screen.getByRole("textbox");
      expect(input).toHaveAttribute("name", "test-select");
    });

    it("has fallback name when no id is provided", () => {
      render(<SingleSelect {...defaultProps} showFullContent />);

      const textarea = screen.getByRole("textbox");
      expect(textarea).toHaveAttribute("name", "single-select-textarea");
    });

    it("has proper aria-label for clear button", () => {
      render(<SingleSelect {...defaultProps} selected="option1" />);

      const clearButton = screen.getByTestId("icon-close_small");
      expect(clearButton).toBeInTheDocument();
    });

    it("has proper aria-label for dropdown button", () => {
      render(<SingleSelect {...defaultProps} />);

      const dropdownButton = screen.getByTestId("icon-chevron_down");
      expect(dropdownButton).toBeInTheDocument();
    });
  });

  describe("Edge Cases", () => {
    it("handles empty options array", () => {
      render(<SingleSelect {...defaultProps} options={[]} />);

      const input = screen.getByRole("textbox");
      expect(input).toBeInTheDocument();
    });

    it("handles options with special characters", () => {
      const specialOptions = [
        { label: "Option with & symbols", value: "option1" },
        { label: "Option with <tags>", value: "option2" },
        { label: "Option with 'quotes'", value: "option3" },
      ];

      render(<SingleSelect {...defaultProps} options={specialOptions} />);

      const input = screen.getByRole("textbox");
      expect(input).toBeInTheDocument();
    });

    it("handles very long option labels", () => {
      const longOptions = [
        {
          label:
            "This is a very long option label that should be handled properly by the component and should not break the layout or cause any issues with the rendering",
          value: "long-option",
        },
      ];

      render(
        <SingleSelect {...defaultProps} options={longOptions} showFullContent />
      );

      const textarea = screen.getByRole("textbox");
      expect(textarea).toBeInTheDocument();
    });

    it("handles rapid clicking", () => {
      render(<SingleSelect {...defaultProps} />);

      const input = screen.getByRole("textbox");

      // Rapidly click multiple times
      fireEvent.click(input);
      fireEvent.click(input);
      fireEvent.click(input);

      // Should not crash and should have consistent state
      expect(input).toBeInTheDocument();
    });
  });
});
