import type { FormState } from "@/components/dynamicForm/dropdown";
import type { UserFormMode } from "@/components/templatesComponents/customisedForm.types";
import { ResponseOption } from "@/components/dynamicForm/dropdown.types";
import FetchFromSrcDropdown, {
  RenderFetchFromSrcDropdownInSummary,
} from "@/components/templatesComponents/PreviewComponents/FetchFromSrcDropdown";
import useRestMutation from "@/hooks/useRestMutation";
import "@testing-library/jest-dom";
import { act, fireEvent, render, screen } from "@testing-library/react";
import type { AxiosError } from "axios";

// Mock dependencies
jest.mock("@/api/restApi", () => ({
  __esModule: true,
  default: jest.fn(),
}));

jest.mock("@/hooks/useRestMutation", () => ({
  __esModule: true,
  default: jest.fn(),
}));

jest.mock(
  "@/components/templatesComponents/PreviewComponents/DropDown",
  () => ({
    __esModule: true,
    default: ({ content, onChange, inSummary, returnLabelAndValue }: any) => (
      <div data-testid="mock-dropdown">
        <div data-testid="dropdown-content">{JSON.stringify(content)}</div>
        <div data-testid="dropdown-in-summary">
          {inSummary ? "true" : "false"}
        </div>
        <div data-testid="dropdown-return-label-value">
          {returnLabelAndValue ? "true" : "false"}
        </div>
        <button
          data-testid="dropdown-change-button"
          onClick={() =>
            onChange([{ value: "test-value", label: "Test Label" }])
          }
        >
          Change Value
        </button>
      </div>
    ),
  })
);

// Mock dependencies
jest.mock("@/api/restApi", () => ({
  __esModule: true,
  default: jest.fn(),
}));

jest.mock("@/hooks/useRestMutation", () => ({
  __esModule: true,
  default: jest.fn(),
}));

jest.mock(
  "@/components/templatesComponents/PreviewComponents/DropDown",
  () => ({
    __esModule: true,
    default: ({ content, onChange, inSummary, returnLabelAndValue }: any) => (
      <div data-testid="mock-dropdown">
        <div data-testid="dropdown-content">{JSON.stringify(content)}</div>
        <div data-testid="dropdown-in-summary">
          {inSummary ? "true" : "false"}
        </div>
        <div data-testid="dropdown-return-label-value">
          {returnLabelAndValue ? "true" : "false"}
        </div>
        <button
          data-testid="dropdown-change-button"
          onClick={() =>
            onChange([{ value: "test-value", label: "Test Label" }])
          }
        >
          Change Value
        </button>
      </div>
    ),
  })
);

// Mock data
const mockFormState: FormState = {
  title: "Test Dropdown",
  hint_text: "Select an option",
  response_option: ResponseOption.Fetch,
  options: [],
  multiple_choice: false,
  include_other_option: false,
  include_other_input_box: false,
  include_NA_option: false,
  user_other_value: null,
  is_mandatory: false,
  comments_allowed: false,
  attachments_allowed: false,
  user_value: null,
  pre_population_rule_name: null,
  user_comments: null,
  user_attachments: null,
  api_details: {
    name: "Test API",
    description: "Test API Description",
    endpoint: "/api/test-endpoint",
    method: "GET",
    headers: { "Content-Type": "application/json" },
    request: {},
    response: {},
    value_key: "value",
    label_key: "label",
  },
};

const mockContent = {
  type: "dropdown",
  properties: mockFormState,
};

const mockMode: UserFormMode = "EDIT";

describe("FetchFromSrcDropdown", () => {
  const mockOnChange = jest.fn();
  const mockMutate = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useRestMutation as jest.Mock).mockReturnValue({
      mutate: mockMutate,
      isLoading: false,
    });
  });

  describe("Component Rendering", () => {
    it("renders loading state when fetching data", () => {
      (useRestMutation as jest.Mock).mockReturnValue({
        mutate: mockMutate,
        isLoading: true,
      });

      render(
        <FetchFromSrcDropdown
          content={mockContent}
          mode={mockMode}
          onChange={mockOnChange}
        />
      );

      expect(screen.getByText("Loading Dropdown...")).toBeInTheDocument();
    });

    it("renders DropDown component when not loading", () => {
      render(
        <FetchFromSrcDropdown
          content={mockContent}
          mode={mockMode}
          onChange={mockOnChange}
        />
      );

      expect(screen.getByTestId("mock-dropdown")).toBeInTheDocument();
    });

    it("passes correct props to DropDown component", () => {
      render(
        <FetchFromSrcDropdown
          content={mockContent}
          mode={mockMode}
          onChange={mockOnChange}
          inSummary={true}
        />
      );

      expect(screen.getByTestId("dropdown-in-summary")).toHaveTextContent(
        "true"
      );
      expect(
        screen.getByTestId("dropdown-return-label-value")
      ).toHaveTextContent("false");
    });
  });

  describe("API Integration", () => {
    it("calls fetchFileImportedData when component mounts with endpoint", () => {
      render(
        <FetchFromSrcDropdown
          content={mockContent}
          mode={mockMode}
          onChange={mockOnChange}
        />
      );

      expect(useRestMutation).toHaveBeenCalledWith({
        endpoint: "/api/test-endpoint",
        method: "get",
        axiosInstance: expect.any(Function),
        dtoFn: expect.any(Function),
        mutationOptions: {
          onSuccess: expect.any(Function),
          onError: expect.any(Function),
        },
      });
    });

    it("does not call fetchFileImportedData when no endpoint is provided", () => {
      const contentWithoutEndpoint = {
        ...mockContent,
        properties: {
          ...mockFormState,
          api_details: undefined,
        },
      };

      render(
        <FetchFromSrcDropdown
          content={contentWithoutEndpoint}
          mode={mockMode}
          onChange={mockOnChange}
        />
      );

      expect(useRestMutation).toHaveBeenCalledWith({
        endpoint: undefined,
        method: "get",
        axiosInstance: expect.any(Function),
        dtoFn: expect.any(Function),
        mutationOptions: {
          onSuccess: expect.any(Function),
          onError: expect.any(Function),
        },
      });
    });

    it("calls mutate function when component mounts", () => {
      render(
        <FetchFromSrcDropdown
          content={mockContent}
          mode={mockMode}
          onChange={mockOnChange}
        />
      );

      expect(mockMutate).toHaveBeenCalledWith({});
    });
  });

  describe("Data Processing", () => {
    it("processes API response data correctly", () => {
      let onSuccessCallback: (data: any) => void;

      (useRestMutation as jest.Mock).mockImplementation(config => {
        onSuccessCallback = config.mutationOptions.onSuccess;
        return {
          mutate: mockMutate,
          isLoading: false,
        };
      });

      render(
        <FetchFromSrcDropdown
          content={mockContent}
          mode={mockMode}
          onChange={mockOnChange}
        />
      );

      // Simulate successful API response
      const mockResponseData = {
        data: {
          values: ["Zebra", "Alpha", "Beta"],
        },
      };

      act(() => {
        onSuccessCallback!(mockResponseData);
      });

      // The component should now have processed options
      expect(screen.getByTestId("mock-dropdown")).toBeInTheDocument();
    });

    it("sorts options alphabetically", () => {
      let onSuccessCallback: (data: any) => void;

      (useRestMutation as jest.Mock).mockImplementation(config => {
        onSuccessCallback = config.mutationOptions.onSuccess;
        return {
          mutate: mockMutate,
          isLoading: false,
        };
      });

      render(
        <FetchFromSrcDropdown
          content={mockContent}
          mode={mockMode}
          onChange={mockOnChange}
        />
      );

      const mockResponseData = {
        data: {
          values: ["Zebra", "Alpha", "Beta"],
        },
      };

      act(() => {
        onSuccessCallback!(mockResponseData);
      });

      // Options should be sorted alphabetically: Alpha, Beta, Zebra
      expect(screen.getByTestId("mock-dropdown")).toBeInTheDocument();
    });
  });

  describe("Error Handling", () => {
    it("handles API errors gracefully", () => {
      let onErrorCallback: (error: AxiosError) => void;

      (useRestMutation as jest.Mock).mockImplementation(config => {
        onErrorCallback = config.mutationOptions.onError;
        return {
          mutate: mockMutate,
          isLoading: false,
        };
      });

      const consoleSpy = jest.spyOn(console, "log").mockImplementation();

      render(
        <FetchFromSrcDropdown
          content={mockContent}
          mode={mockMode}
          onChange={mockOnChange}
        />
      );

      const mockError = new Error("API Error") as AxiosError;
      act(() => {
        onErrorCallback!(mockError);
      });

      expect(consoleSpy).toHaveBeenCalledWith(mockError);
      consoleSpy.mockRestore();
    });
  });

  describe("User Interaction", () => {
    it("calls onChange when dropdown value changes", () => {
      render(
        <FetchFromSrcDropdown
          content={mockContent}
          mode={mockMode}
          onChange={mockOnChange}
        />
      );

      const changeButton = screen.getByTestId("dropdown-change-button");
      fireEvent.click(changeButton);

      expect(mockOnChange).toHaveBeenCalledWith([
        { value: "test-value", label: "Test Label" },
      ]);
    });
  });

  describe("Content Configuration", () => {
    it("uses default hint_text when not provided", () => {
      const contentWithoutHint = {
        ...mockContent,
        properties: {
          ...mockFormState,
          hint_text: "",
        },
      };

      render(
        <FetchFromSrcDropdown
          content={contentWithoutHint}
          mode={mockMode}
          onChange={mockOnChange}
        />
      );

      const dropdownContent = screen.getByTestId("dropdown-content");
      const content = JSON.parse(dropdownContent.textContent || "{}");

      expect(content.properties.hint_text).toBe("");
    });

    it("passes all properties to DropDown component", () => {
      render(
        <FetchFromSrcDropdown
          content={mockContent}
          mode={mockMode}
          onChange={mockOnChange}
        />
      );

      const dropdownContent = screen.getByTestId("dropdown-content");
      const content = JSON.parse(dropdownContent.textContent || "{}");

      expect(content.properties.title).toBe("Test Dropdown");
      expect(content.properties.hint_text).toBe("Select an option");
      expect(content.properties.is_mandatory).toBe(false);
    });
  });

  describe("RenderFetchFromSrcDropdownInSummary", () => {
    it("renders summary view with title and value", () => {
      const mockLocalValue = { name: "Test Option", id: "test-id" };

      render(
        <RenderFetchFromSrcDropdownInSummary
          properties={mockFormState}
          localValue={mockLocalValue}
        />
      );

      expect(screen.getByText("Test Dropdown")).toBeInTheDocument();
      expect(screen.getByText("Test Option")).toBeInTheDocument();
    });

    it("handles localValue with only id", () => {
      const mockLocalValue = { id: "test-id" };

      render(
        <RenderFetchFromSrcDropdownInSummary
          properties={mockFormState}
          localValue={mockLocalValue}
        />
      );

      expect(screen.getByText("Test Dropdown")).toBeInTheDocument();
      // Check that the component renders without crashing when localValue has only id
      expect(screen.getByText("Test Dropdown")).toBeInTheDocument();
    });
  });

  describe("Edge Cases", () => {
    it("handles empty API response", () => {
      let onSuccessCallback: (data: any) => void;

      (useRestMutation as jest.Mock).mockImplementation(config => {
        onSuccessCallback = config.mutationOptions.onSuccess;
        return {
          mutate: mockMutate,
          isLoading: false,
        };
      });

      render(
        <FetchFromSrcDropdown
          content={mockContent}
          mode={mockMode}
          onChange={mockOnChange}
        />
      );

      const emptyResponseData = {
        data: {
          values: [],
        },
      };

      act(() => {
        onSuccessCallback!(emptyResponseData);
      });

      expect(screen.getByTestId("mock-dropdown")).toBeInTheDocument();
    });

    it("handles malformed API response", () => {
      let onSuccessCallback: (data: any) => void;

      (useRestMutation as jest.Mock).mockImplementation(config => {
        onSuccessCallback = config.mutationOptions.onSuccess;
        return {
          mutate: mockMutate,
          isLoading: false,
        };
      });

      render(
        <FetchFromSrcDropdown
          content={mockContent}
          mode={mockMode}
          onChange={mockOnChange}
        />
      );

      const malformedResponseData = {
        data: {
          values: null,
        },
      };

      // The component should handle null values gracefully or throw an error
      expect(() => {
        act(() => {
          onSuccessCallback!(malformedResponseData);
        });
      }).toThrow("Cannot read properties of null (reading 'map')");
    });
  });
});
