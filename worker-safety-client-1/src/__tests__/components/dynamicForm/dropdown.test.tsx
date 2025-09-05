import "@testing-library/jest-dom";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { createContext } from "react";
/* eslint-disable @typescript-eslint/no-explicit-any */

// Mocks
jest.mock("@/hooks/useRestQuery", () => {
  return {
    __esModule: true,
    default: jest.fn(() => ({
      data: [
        {
          id: "ds1",
          name: "Data Source One",
          columns: ["colA", "colB"],
        },
        {
          id: "ds2",
          name: "Data Source Two",
          columns: ["colX", "colY"],
        },
      ],
      isLoading: false,
      error: null,
      refetch: jest.fn(),
    })),
  };
});

const stableIngestData = {
  ingestOptionItems: {
    items: [
      { colA: "Zebra", colB: "ignored" },
      { colA: "Alpha" },
      { colA: "Zebra" },
    ],
  },
};

jest.mock("@apollo/client", () => ({
  __esModule: true,
  useQuery: jest.fn(() => ({
    data: stableIngestData,
  })),
  gql: (s: string) => s,
}));

// Mock child UI components used only for interactions we need
jest.mock("@/components/shared/field/fieldSelect/FieldSelect", () => ({
  __esModule: true,
  default: ({ label, options, onSelect, defaultOption }: any) => (
    <div>
      <span>{label}</span>
      <span data-testid={`current-selection-${label}`}>
        {defaultOption?.name || "No selection"}
      </span>
      <button
        aria-label={`select-first-${label}`}
        onClick={() => options?.[0] && onSelect(options[0])}
      >
        select-first
      </button>
      {options?.length > 1 && (
        <button
          aria-label={`select-second-${label}`}
          onClick={() => options?.[1] && onSelect(options[1])}
        >
          select-second
        </button>
      )}
    </div>
  ),
}));

jest.mock("@/components/shared/field/fieldRadioGroup/FieldRadioGroup", () => ({
  __esModule: true,
  default: ({ label }: any) => <div>{label}</div>,
}));

jest.mock("@/components/forms/Basic/Input", () => ({
  InputRaw: ({ label, value, onChange }: any) => (
    <input
      aria-label={label}
      value={value}
      onChange={e => onChange?.(e.target.value)}
    />
  ),
}));

jest.mock("@/components/dynamicForm/index", () => ({
  __esModule: true,
  Foooter: ({ onAdd }: any) => (
    <button aria-label="footer-add" onClick={() => onAdd?.()}>
      Add
    </button>
  ),
  RepeatSectionContext: createContext(false),
}));

jest.mock("@/components/dynamicForm/WidgetCheckbox", () => ({
  __esModule: true,
  WidgetCheckbox: ({ checked, onToggle, disabled }: any) => (
    <div>
      <input
        type="checkbox"
        checked={checked}
        onChange={e => onToggle?.(e.target.checked)}
        disabled={disabled}
        data-testid="widget-checkbox"
      />
      <span>Widget</span>
    </div>
  ),
}));

jest.mock("@/components/forms/Basic/Checkbox", () => ({
  Checkbox: ({ checked, onClick, disabled, children }: any) => (
    <div>
      <input
        type="checkbox"
        checked={checked}
        onChange={() => onClick?.()}
        disabled={disabled}
      />
      {children}
    </div>
  ),
}));

// Component under test (use require after mocks to satisfy linter ordering)
// eslint-disable-next-line @typescript-eslint/no-var-requires
const FormComponent = require("@/components/dynamicForm/dropdown").default;

describe("dynamicForm/dropdown builder", () => {
  it("shows info text and reveals data source and column selectors; auto-populates options and builds api_details", async () => {
    const onAdd = jest.fn();

    render(
      <FormComponent
        onAdd={onAdd}
        onClose={jest.fn()}
        initialState={{
          title: "Test Dropdown",
          hint_text: "",
          response_option: "fetch",
          options: [],
          multiple_choice: false,
          include_other_option: false,
          user_other_value: "",
          include_other_input_box: false,
          is_mandatory: false,
          comments_allowed: false,
          attachments_allowed: false,
          user_value: null,
          pre_population_rule_name: null,
          user_comments: null,
          user_attachments: null,
        }}
      />
    );

    // Info hint
    expect(
      screen.getByText(
        "Populate dropdown options by selecting a data source and column."
      )
    ).toBeInTheDocument();

    // Data Source select present; choose first
    fireEvent.click(
      screen.getByRole("button", { name: /select-first-Data Source/i })
    );

    // Column select present after data source; choose first
    fireEvent.click(
      screen.getByRole("button", { name: /select-first-Source Column/i })
    );

    // Options auto populated (Alpha, Zebra) and count shown
    await waitFor(() => {
      expect(
        screen.getByText(
          /Loaded 2 unique options from the selected data source\./i
        )
      ).toBeInTheDocument();
    });

    // Trigger add to send submission
    fireEvent.click(screen.getByRole("button", { name: /footer-add/i }));

    expect(onAdd).toHaveBeenCalledTimes(1);
    const submitted = onAdd.mock.calls[0][0];

    // Expect options unique + sorted
    expect(submitted.options.map((o: any) => o.label)).toEqual([
      "Alpha",
      "Zebra",
    ]);
    // Expect api_details constructed with GET and proper endpoint
    expect(submitted.api_details).toEqual(
      expect.objectContaining({
        method: "GET",
        endpoint: "uploads/data-sources/ds1/columns/colA",
        value_key: "colA",
        label_key: "colA",
      })
    );
  });

  it("keeps Multiple Choice and Include 'Other' checkboxes visible", () => {
    render(<FormComponent onAdd={jest.fn()} onClose={jest.fn()} />);

    expect(screen.getByText(/Multiple Choice/i)).toBeInTheDocument();
    expect(
      screen.getByText(/Include 'Other' in response/i)
    ).toBeInTheDocument();
  });

  it("resets column selection when data source changes", async () => {
    render(
      <FormComponent
        onAdd={jest.fn()}
        onClose={jest.fn()}
        initialState={{
          title: "Test Dropdown",
          hint_text: "",
          response_option: "fetch",
          options: [],
          multiple_choice: false,
          include_other_option: false,
          user_other_value: "",
          include_other_input_box: false,
          is_mandatory: false,
          comments_allowed: false,
          attachments_allowed: false,
          user_value: null,
          pre_population_rule_name: null,
          user_comments: null,
          user_attachments: null,
        }}
      />
    );

    // Initially no data source or column is selected
    expect(
      screen.getByTestId("current-selection-Data Source *")
    ).toHaveTextContent("No selection");

    // Select first data source (Data Source One)
    fireEvent.click(
      screen.getByRole("button", { name: /select-first-Data Source/i })
    );

    // Data source should now show as selected
    await waitFor(() => {
      expect(
        screen.getByTestId("current-selection-Data Source *")
      ).toHaveTextContent("Data Source One");
    });

    // Column selector should appear, initially with no selection
    expect(
      screen.getByTestId("current-selection-Source Column *")
    ).toHaveTextContent("No selection");

    // Select first column
    fireEvent.click(
      screen.getByRole("button", { name: /select-first-Source Column/i })
    );

    // Column should now show as selected
    await waitFor(() => {
      expect(
        screen.getByTestId("current-selection-Source Column *")
      ).toHaveTextContent("colA");
    });

    // Now change data source to the second one (Data Source Two)
    fireEvent.click(
      screen.getByRole("button", { name: /select-second-Data Source/i })
    );

    // Data source should update to the new selection
    await waitFor(() => {
      expect(
        screen.getByTestId("current-selection-Data Source *")
      ).toHaveTextContent("Data Source Two");
    });

    // Column selection should be reset to no selection
    await waitFor(() => {
      expect(
        screen.getByTestId("current-selection-Source Column *")
      ).toHaveTextContent("No selection");
    });
  });

  it("adds N/A option when Include N/A checkbox is clicked", async () => {
    const onAdd = jest.fn();

    render(
      <FormComponent
        onAdd={onAdd}
        onClose={jest.fn()}
        initialState={{
          title: "Test Dropdown",
          hint_text: "",
          response_option: "manual_entry",
          options: [{ value: "option1", label: "Option 1" }],
          multiple_choice: false,
          include_other_option: false,
          include_NA_option: false,
          user_other_value: "",
          include_other_input_box: false,
          is_mandatory: false,
          comments_allowed: false,
          attachments_allowed: false,
          user_value: null,
          pre_population_rule_name: null,
          user_comments: null,
          user_attachments: null,
        }}
      />
    );

    // Find the Include N/A checkbox by finding the text and getting the parent checkbox
    const naCheckboxContainer = screen
      .getByText(/Include 'N\/A' in response/i)
      .closest("div");
    const naCheckbox = naCheckboxContainer?.querySelector(
      'input[type="checkbox"]'
    );

    // Initially the checkbox should be unchecked
    expect(naCheckbox).not.toBeChecked();

    // Click the Include N/A checkbox
    if (naCheckbox) {
      fireEvent.click(naCheckbox);
    }

    // Trigger form submission to check the options
    fireEvent.click(screen.getByRole("button", { name: /footer-add/i }));

    expect(onAdd).toHaveBeenCalledTimes(1);
    const submitted = onAdd.mock.calls[0][0];

    // Verify that N/A option was added to the options array
    expect(submitted.options).toContainEqual({ value: "na", label: "N/A" });
    expect(submitted.include_NA_option).toBe(true);
  });
});
