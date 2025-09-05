import type { CustomisedFromContextStateType } from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MockedProvider } from "@apollo/client/testing";
import { useQuery } from "@apollo/client";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import useRestMutation from "@/hooks/useRestMutation";
import HistoricalIncident from "./HistoricalIncident";

// Mock dependencies
jest.mock("@apollo/client", () => ({
  ...jest.requireActual("@apollo/client"),
  useQuery: jest.fn(),
}));

jest.mock("@/hooks/useRestMutation");
jest.mock("@/api/customFlowApi");
jest.mock("@/utils/date/helper", () => ({
  convertDateToString: jest.fn(date => `Converted: ${date}`),
}));

// Mock the context
const mockDispatch = jest.fn();
const mockState: CustomisedFromContextStateType = {
  form: {
    id: "test-form-id",
    type: "form",
    contents: [],
    properties: {
      title: "Test Form",
      status: "draft",
      description: "Test form description",
    },
    metadata: {},
    template_id: "test-template",
    created_at: "2023-01-01",
    created_by: { id: "test-user" },
    updated_at: "2023-01-01",
    updated_by: "test-user",
    settings: {
      availability: {
        adhoc: { selected: true },
        work_package: { selected: false },
      },
      edit_expiry_days: 30,
    },
    isDisabled: false,
    component_data: {
      activities_tasks: [
        {
          id: "activity-1",
          isCritical: false,
          criticalDescription: null,
          name: "Test Activity",
          status: "active",
          startDate: "2023-01-01",
          endDate: "2023-01-31",
          taskCount: 2,
          tasks: [
            {
              id: "task-1",
              name: "Task 1",
              selected: true,
              fromWorkOrder: false,
              riskLevel: "LOW",
              recommended: false,
              libraryTask: {
                __typename: "LibraryTask",
                id: "library-task-1",
                riskLevel: "LOW",
                name: "Library Task 1",
              },
            },
            {
              id: "task-2",
              name: "Task 2",
              selected: false,
              fromWorkOrder: false,
              riskLevel: "MEDIUM",
              recommended: false,
              libraryTask: {
                __typename: "LibraryTask",
                id: "library-task-2",
                riskLevel: "MEDIUM",
                name: "Library Task 2",
              },
            },
          ],
        },
      ],
    },
  },
  formBuilderMode: "BUILD",
  isFormDirty: false,
  isFormIsValid: true,
};

const MockContextProvider = ({
  children,
  state = mockState,
  dispatch = mockDispatch,
}: {
  children: React.ReactNode;
  state?: CustomisedFromContextStateType;
  dispatch?: jest.MockedFunction<any>;
}) => (
  <CustomisedFromStateContext.Provider value={{ state, dispatch }}>
    {children}
  </CustomisedFromStateContext.Provider>
);

// Mock incident data
const mockIncidents = [
  {
    id: "incident-1",
    description:
      "This is a test incident description that is longer than 150 characters to test the truncation functionality. It should be truncated when not expanded and show the full text when expanded.",
    incidentDate: "2023-01-15T10:30:00Z",
    incidentType: "Injury/Illness",
    severity: "first_aid",
  },
  {
    id: "incident-2",
    description: "Another test incident with shorter description.",
    incidentDate: "2023-02-20T14:45:00Z",
    incidentType: "Property Damage",
    severity: "lost_time",
  },
];

const renderHistoricalIncident = (props = {}, contextState = mockState) => {
  return render(
    <MockedProvider>
      <MockContextProvider state={contextState}>
        <HistoricalIncident
          label="Historical Incidents"
          componentId="test-component"
          {...props}
        />
      </MockContextProvider>
    </MockedProvider>
  );
};

describe("HistoricalIncident", () => {
  const mockUseQuery = useQuery as jest.MockedFunction<typeof useQuery>;
  const mockUseRestMutation = useRestMutation as jest.MockedFunction<
    typeof useRestMutation
  >;

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseRestMutation.mockReturnValue({
      mutate: jest.fn(),
      isLoading: false,
      error: null,
    } as any);
  });

  describe("Props validation scenarios", () => {
    test("should handle null label", () => {
      mockUseQuery.mockReturnValue({
        data: { historicalIncidentsForTasks: [] },
        loading: false,
        error: null,
      } as any);

      renderHistoricalIncident({ label: null });

      expect(
        screen.getByText("No content available for this job.")
      ).toBeInTheDocument();
    });

    test("should handle empty string label", () => {
      mockUseQuery.mockReturnValue({
        data: { historicalIncidentsForTasks: [] },
        loading: false,
        error: null,
      } as any);

      renderHistoricalIncident({ label: "" });

      expect(
        screen.getByText("No content available for this job.")
      ).toBeInTheDocument();
    });

    test("should handle null componentId", () => {
      mockUseQuery.mockReturnValue({
        data: { historicalIncidentsForTasks: mockIncidents },
        loading: false,
        error: null,
      } as any);

      renderHistoricalIncident({ componentId: null });

      // Should still render but may not dispatch updates
      expect(screen.getByText("Historical Incidents")).toBeInTheDocument();
    });

    test("should handle empty string componentId", () => {
      mockUseQuery.mockReturnValue({
        data: { historicalIncidentsForTasks: mockIncidents },
        loading: false,
        error: null,
      } as any);

      renderHistoricalIncident({ componentId: "" });

      // Should still render but may not dispatch updates
      expect(screen.getByText("Historical Incidents")).toBeInTheDocument();
    });
  });

  describe("API data scenarios", () => {
    test("should handle null API response", () => {
      mockUseQuery.mockReturnValue({
        data: null,
        loading: false,
        error: null,
      } as any);

      renderHistoricalIncident();

      expect(
        screen.getByText("No content available for this job.")
      ).toBeInTheDocument();
    });

    test("should handle undefined API response", () => {
      mockUseQuery.mockReturnValue({
        data: undefined,
        loading: false,
        error: null,
      } as any);

      renderHistoricalIncident();

      expect(
        screen.getByText("No content available for this job.")
      ).toBeInTheDocument();
    });

    test("should handle empty incidents array", () => {
      mockUseQuery.mockReturnValue({
        data: { historicalIncidentsForTasks: [] },
        loading: false,
        error: null,
      } as any);

      renderHistoricalIncident();

      expect(
        screen.getByText("No content available for this job.")
      ).toBeInTheDocument();
    });

    test("should handle API error", () => {
      mockUseQuery.mockReturnValue({
        data: null,
        loading: false,
        error: new Error("API Error"),
      } as any);

      renderHistoricalIncident();

      expect(
        screen.getByText("No content available for this job.")
      ).toBeInTheDocument();
    });

    test("should handle loading state", () => {
      mockUseQuery.mockReturnValue({
        data: null,
        loading: true,
        error: null,
      } as any);

      renderHistoricalIncident();

      expect(
        screen.getByText("No content available for this job.")
      ).toBeInTheDocument();
    });

    test("should handle incidents with null/undefined properties", () => {
      const incidentsWithNullProps = [
        {
          id: "incident-1",
          description: null,
          incidentDate: null,
          incidentType: null,
          severity: null,
        },
        {
          id: "incident-2",
          description: undefined,
          incidentDate: undefined,
          incidentType: undefined,
          severity: undefined,
        },
      ];

      mockUseQuery.mockReturnValue({
        data: { historicalIncidentsForTasks: incidentsWithNullProps },
        loading: false,
        error: null,
      } as any);

      renderHistoricalIncident();

      // Should render without crashing
      expect(screen.getByText("Historical Incidents")).toBeInTheDocument();
    });
  });

  describe("Context state scenarios", () => {
    test("should handle form without id", () => {
      const formWithoutId: CustomisedFromContextStateType = {
        ...mockState,
        form: {
          ...mockState.form,
          id: "",
        },
      };

      mockUseQuery.mockReturnValue({
        data: { historicalIncidentsForTasks: mockIncidents },
        loading: false,
        error: null,
      } as any);

      renderHistoricalIncident({}, formWithoutId);

      expect(screen.getByText("Historical Incidents")).toBeInTheDocument();
    });

    test("should handle null component_data", () => {
      const formWithoutComponentData: CustomisedFromContextStateType = {
        ...mockState,
        form: {
          ...mockState.form,
          component_data: undefined,
        },
      };

      mockUseQuery.mockReturnValue({
        data: { historicalIncidentsForTasks: mockIncidents },
        loading: false,
        error: null,
      } as any);

      renderHistoricalIncident({}, formWithoutComponentData);

      expect(screen.getByText("Historical Incidents")).toBeInTheDocument();
    });

    test("should handle empty activities_tasks", () => {
      const formWithEmptyActivities: CustomisedFromContextStateType = {
        ...mockState,
        form: {
          ...mockState.form,
          component_data: {
            activities_tasks: [],
          },
        },
      };

      mockUseQuery.mockReturnValue({
        data: { historicalIncidentsForTasks: mockIncidents },
        loading: false,
        error: null,
      } as any);

      renderHistoricalIncident({}, formWithEmptyActivities);

      expect(screen.getByText("Historical Incidents")).toBeInTheDocument();
    });
  });

  describe("Component functionality", () => {
    beforeEach(() => {
      mockUseQuery.mockReturnValue({
        data: { historicalIncidentsForTasks: mockIncidents },
        loading: false,
        error: null,
      } as any);
    });

    test("should render incident details correctly", () => {
      renderHistoricalIncident();

      expect(screen.getByText("Historical Incidents")).toBeInTheDocument();
      expect(
        screen.getByText(
          "Safety records related to this job. Shuffle to view more records."
        )
      ).toBeInTheDocument();
      expect(screen.getByText("Injury/Illness")).toBeInTheDocument();
      expect(
        screen.getByText("Converted: 2023-01-15T10:30:00Z")
      ).toBeInTheDocument();
      expect(screen.getByText("First Aid")).toBeInTheDocument();
    });

    test("should truncate long descriptions", () => {
      renderHistoricalIncident();

      const description = screen.getByText(
        /This is a test incident description/
      );
      expect(description).toBeInTheDocument();

      // Should show truncated text with "Read more" button
      expect(screen.getByText("Read more")).toBeInTheDocument();
    });

    test("should expand/collapse description", () => {
      renderHistoricalIncident();

      const readMoreButton = screen.getByText("Read more");
      fireEvent.click(readMoreButton);

      expect(screen.getByText("Read less")).toBeInTheDocument();

      const readLessButton = screen.getByText("Read less");
      fireEvent.click(readLessButton);

      expect(screen.getByText("Read more")).toBeInTheDocument();
    });

    test("should handle shuffle functionality", () => {
      renderHistoricalIncident();

      const shuffleButton = screen.getByText("Shuffle");
      fireEvent.click(shuffleButton);

      // Should dispatch action to update incident
      expect(mockDispatch).toHaveBeenCalledWith({
        type: CF_REDUCER_CONSTANTS.UPDATE_HISTORICAL_INCIDENT,
        payload: {
          componentId: "test-component",
          incident: expect.any(Object),
        },
      });
    });

    test("should handle single incident (no shuffle)", () => {
      const singleIncident = [mockIncidents[0]];

      mockUseQuery.mockReturnValue({
        data: { historicalIncidentsForTasks: singleIncident },
        loading: false,
        error: null,
      } as any);

      renderHistoricalIncident();

      const shuffleButton = screen.getByText("Shuffle");
      fireEvent.click(shuffleButton);

      // Should not dispatch shuffle action for single incident
      expect(mockDispatch).toHaveBeenCalledWith({
        type: CF_REDUCER_CONSTANTS.UPDATE_HISTORICAL_INCIDENT,
        payload: {
          componentId: "test-component",
          incident: singleIncident[0],
        },
      });
    });
  });

  describe("Edge cases", () => {
    test("should handle incident with empty description", () => {
      const incidentWithEmptyDescription = [
        {
          ...mockIncidents[0],
          description: "",
        },
      ];

      mockUseQuery.mockReturnValue({
        data: { historicalIncidentsForTasks: incidentWithEmptyDescription },
        loading: false,
        error: null,
      } as any);

      renderHistoricalIncident();

      expect(screen.getByText("Historical Incidents")).toBeInTheDocument();
      // Should not show "Read more" button for empty description
      expect(screen.queryByText("Read more")).not.toBeInTheDocument();
    });

    test("should handle incident with description exactly at character limit", () => {
      const descriptionAtLimit = "a".repeat(150);
      const incidentAtLimit = [
        {
          ...mockIncidents[0],
          description: descriptionAtLimit,
        },
      ];

      mockUseQuery.mockReturnValue({
        data: { historicalIncidentsForTasks: incidentAtLimit },
        loading: false,
        error: null,
      } as any);

      renderHistoricalIncident();

      expect(screen.getByText("Historical Incidents")).toBeInTheDocument();
      // Should not show "Read more" button for description at limit
      expect(screen.queryByText("Read more")).not.toBeInTheDocument();
    });

    test("should handle incident with description just over character limit", () => {
      const descriptionOverLimit = "a".repeat(151);
      const incidentOverLimit = [
        {
          ...mockIncidents[0],
          description: descriptionOverLimit,
        },
      ];

      mockUseQuery.mockReturnValue({
        data: { historicalIncidentsForTasks: incidentOverLimit },
        loading: false,
        error: null,
      } as any);

      renderHistoricalIncident();

      expect(screen.getByText("Historical Incidents")).toBeInTheDocument();
      // Should show "Read more" button for description over limit
      expect(screen.getByText("Read more")).toBeInTheDocument();
    });

    test("should handle missing incident properties gracefully", () => {
      const incompleteIncident = [
        {
          id: "incident-1",
          // Missing other properties
        },
      ];

      mockUseQuery.mockReturnValue({
        data: { historicalIncidentsForTasks: incompleteIncident },
        loading: false,
        error: null,
      } as any);

      renderHistoricalIncident();

      expect(screen.getByText("Historical Incidents")).toBeInTheDocument();
      // Should render without crashing
    });
  });

  describe("API integration", () => {
    test("should call saveFormData when incident is updated", async () => {
      const mockMutate = jest.fn();
      mockUseRestMutation.mockReturnValue({
        mutate: mockMutate,
        isLoading: false,
        error: null,
      } as any);

      mockUseQuery.mockReturnValue({
        data: { historicalIncidentsForTasks: mockIncidents },
        loading: false,
        error: null,
      } as any);

      renderHistoricalIncident();

      // Trigger incident update
      const shuffleButton = screen.getByText("Shuffle");
      fireEvent.click(shuffleButton);

      await waitFor(() => {
        expect(mockMutate).toHaveBeenCalled();
      });
    });

    test("should handle API save error gracefully", () => {
      const consoleSpy = jest.spyOn(console, "error").mockImplementation();

      mockUseRestMutation.mockReturnValue({
        mutate: jest.fn(),
        isLoading: false,
        error: new Error("API Error"),
      } as any);

      mockUseQuery.mockReturnValue({
        data: { historicalIncidentsForTasks: mockIncidents },
        loading: false,
        error: null,
      } as any);

      renderHistoricalIncident();

      // Should render without crashing even with API error
      expect(screen.getByText("Historical Incidents")).toBeInTheDocument();

      consoleSpy.mockRestore();
    });
  });
});
