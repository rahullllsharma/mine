import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import Filters from "./Filters";

// Mock the dependencies
jest.mock("../../../hooks/useRestMutation", () => ({
  __esModule: true,
  default: () => ({
    mutate: jest.fn(),
  }),
}));

jest.mock("../../../api/customFlowApi", () => ({}));

jest.mock("@/pages/templates", () => ({
  getDateFilterField: jest.fn(() => ({ from: null, to: null })),
  getFilterField: jest.fn(() => []),
}));

jest.mock("@/components/flyover/Flyover", () => {
  return function MockFlyover({ children, isOpen, onClose, footer }: any) {
    if (!isOpen) return null;
    return (
      <div data-testid="flyover">
        <button data-testid="close-button" onClick={onClose}>
          Close
        </button>
        {children}
        {footer}
      </div>
    );
  };
});

jest.mock(
  "@/components/templatesComponents/filterSection/FilterSection",
  () => {
    return function MockFilterSection({ children, title }: any) {
      return (
        <div data-testid="filter-section">
          <h3>{title}</h3>
          {children}
        </div>
      );
    };
  }
);

jest.mock("@/components/shared/inputSelect/multiSelect/MultiSelect", () => {
  return function MockMultiSelect({ value, onSelect, placeholder }: any) {
    return (
      <div data-testid="multi-select">
        <input
          data-testid="multi-select-input"
          placeholder={placeholder}
          onChange={e => {
            const newValue = e.target.value
              ? [{ id: "1", name: e.target.value }]
              : [];
            onSelect(newValue);
          }}
        />
        <div data-testid="selected-values">
          {value?.map((item: any) => item.name).join(", ")}
        </div>
      </div>
    );
  };
});

jest.mock("@/components/shared/inputDateSelect/InputDateSelect", () => {
  return function MockInputDateSelect({ onDateChange, placeholder }: any) {
    return (
      <input
        data-testid="date-select"
        placeholder={placeholder}
        type="date"
        onChange={e =>
          onDateChange(e.target.value ? new Date(e.target.value) : null)
        }
      />
    );
  };
});

jest.mock("@/components/shared/button/tertiary/ButtonTertiary", () => {
  return function MockButtonTertiary({ label, onClick }: any) {
    return (
      <button data-testid="cancel-button" onClick={onClick}>
        {label}
      </button>
    );
  };
});

jest.mock("@/components/shared/button/primary/ButtonPrimary", () => {
  return function MockButtonPrimary({ label, onClick }: any) {
    return (
      <button data-testid="apply-button" onClick={onClick}>
        {label}
      </button>
    );
  };
});

describe("Filters Component", () => {
  const mockFiltersValues = [
    {
      field: "TEMPLATENAME" as const,
      values: [],
    },
    {
      field: "PUBLISHEDBY" as const,
      values: [],
    },
    {
      field: "PUBLISHEDON" as const,
      values: { from: null, to: null },
    },
  ];

  const defaultProps = {
    data: {},
    isOpen: true,
    onClose: jest.fn(),
    onApply: jest.fn(),
    filtersValues: mockFiltersValues,
    onClear: jest.fn(),
    onChangeFilter: jest.fn(),
    type: "published" as const,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should reset filters to applied state when cancel is clicked", async () => {
    const onChangeFilter = jest.fn();
    const onClose = jest.fn();

    render(
      <Filters
        {...defaultProps}
        onChangeFilter={onChangeFilter}
        onClose={onClose}
      />
    );

    // Simulate user making a filter selection
    const multiSelectInput = screen.getAllByTestId("multi-select-input")[0];
    fireEvent.change(multiSelectInput, { target: { value: "Test Template" } });

    // Click cancel
    const cancelButton = screen.getByTestId("cancel-button");
    fireEvent.click(cancelButton);

    // Verify that onChangeFilter was called to reset the filters
    await waitFor(() => {
      expect(onChangeFilter).toHaveBeenCalled();
    });

    // Verify that onClose was called
    expect(onClose).toHaveBeenCalled();
  });

  it("should apply working filters when apply is clicked", async () => {
    const onApply = jest.fn();
    const onChangeFilter = jest.fn();

    render(
      <Filters
        {...defaultProps}
        onApply={onApply}
        onChangeFilter={onChangeFilter}
      />
    );

    // Simulate user making a filter selection
    const multiSelectInput = screen.getAllByTestId("multi-select-input")[0];
    fireEvent.change(multiSelectInput, { target: { value: "Test Template" } });

    // Click apply
    const applyButton = screen.getByTestId("apply-button");
    fireEvent.click(applyButton);

    // Verify that onApply was called
    await waitFor(() => {
      expect(onApply).toHaveBeenCalled();
    });

    // Verify that onChangeFilter was called to update parent state
    expect(onChangeFilter).toHaveBeenCalled();
  });

  it("should handle clear filters correctly", () => {
    const onClear = jest.fn();

    render(<Filters {...defaultProps} onClear={onClear} />);

    // Click clear all button
    const clearButton = screen.getByText("Clear all");
    fireEvent.click(clearButton);

    // Verify that onClear was called
    expect(onClear).toHaveBeenCalled();
  });

  it("should close flyover when close button is clicked", () => {
    const onClose = jest.fn();
    const onChangeFilter = jest.fn();

    render(
      <Filters
        {...defaultProps}
        onClose={onClose}
        onChangeFilter={onChangeFilter}
      />
    );

    // Click the flyover close button (X button)
    const closeButton = screen.getByTestId("close-button");
    fireEvent.click(closeButton);

    // Verify that the cancel logic was triggered
    expect(onChangeFilter).toHaveBeenCalled();
    expect(onClose).toHaveBeenCalled();
  });
});
