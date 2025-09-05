import React, { useState } from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import CustomisedFromStateContext, { type CustomisedFromContextStateType } from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import { FORM_EVENTS, formEventEmitter } from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import { UserFormModeTypes, type FormBuilderModeProps } from "../../customisedForm.types";
import DateTime from "./DateTime";

// Mocks
jest.mock("next/router", () => ({
  useRouter: jest.fn(),
}));

jest.mock("@apollo/client", () => ({
  gql: jest.fn(),
  useMutation: () => [jest.fn()],
}));

jest.mock("@/hooks/useCWFFormState", () => ({
  __esModule: true,
  default: () => ({ setCWFFormStateDirty: jest.fn() }),
}));

const { useRouter } = jest.requireMock("next/router");

const buildContextState = (): CustomisedFromContextStateType => ({
  form: {
    id: "form-id",
    type: "FORM",
    properties: {
      title: "Form title",
      description: "",
      status: "in_progress",
      report_start_date: undefined,
    },
    contents: [],
    settings: {
      availability: {
        adhoc: { selected: true },
        work_package: { selected: true },
      },
      edit_expiry_days: 0,
    },
    isDisabled: false,
    component_data: {
      activities_tasks: [],
      hazards_controls: {
        tasks: [],
        manually_added_hazards: [],
        site_conditions: [],
      },
      site_conditions: [],
      location_data: {
        name: "",
        description: "",
        manual_location: false,
        gps_coordinates: null,
      },
    },
    metadata: { work_package: { id: "wp-1" } },
  },
  formBuilderMode: "BUILD" as FormBuilderModeProps,
  isFormDirty: false,
  isFormIsValid: true,
});

const ToastProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => (
  <ToastContext.Provider
    value={{ items: [], pushToast: jest.fn(), dismissToast: jest.fn() }}
  >
    {children}
  </ToastContext.Provider>
);

describe("DateTime (report date integration)", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("1) dispatches CHANGE_INITIAL_STATE with updated properties.report_start_date on manual change when reportDate is true", () => {
    const dispatch = jest.fn();
    (useRouter as jest.Mock).mockReturnValue({ query: {} });

    const properties = {
      title: "Report Date",
      is_mandatory: false,
      comments_allowed: false,
      attachments_allowed: false,
      selected_type: "date_only" as const,
      date_response_type: "calendar" as const,
      date_options: "single_date" as const,
      date_type: "single_date" as const,
      user_value: null,
      user_comments: null,
      user_attachments: null,
    } as any;

    render(
      <ToastProvider>
        <CustomisedFromStateContext.Provider
          value={{ state: buildContextState(), dispatch }}
        >
          <DateTime
            content={{ type: "input_date_time" as any, properties }}
            mode={UserFormModeTypes.EDIT}
            onChange={jest.fn()}
            withConfirmationDialog={false}
            reportDate={true}
          />
        </CustomisedFromStateContext.Provider>
      </ToastProvider>
    );

    // Since there are multiple inputs with empty value, get the one with the specific id
    const inputs = screen.getAllByDisplayValue("");
    const targetInput = inputs.find(input => input.id === "Report Date") as HTMLInputElement;
    fireEvent.change(targetInput, { target: { value: "2025-01-01" } });

    expect(dispatch).toHaveBeenCalledWith(
      expect.objectContaining({
        type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
        payload: expect.objectContaining({
          properties: expect.objectContaining({
            report_start_date: "2025-01-01",
          }),
        }),
      })
    );
  });

  it("2) updates report_start_date on initial load via auto-populate when startDate is present (useEffect on mount)", () => {
    const dispatch = jest.fn();
    // Provide startDate via router to trigger auto-population path
    (useRouter as jest.Mock).mockReturnValue({
      query: { startDate: "2024-03-15" },
    });

    const properties = {
      title: "Report Date",
      is_mandatory: false,
      comments_allowed: false,
      attachments_allowed: false,
      selected_type: "date_only" as const,
      date_response_type: "auto_populate_current_date" as const,
      date_options: "single_date" as const,
      date_type: "single_date" as const,
      user_value: null,
      user_comments: null,
      user_attachments: null,
    } as any;

    render(
      <ToastProvider>
        <CustomisedFromStateContext.Provider
          value={{ state: buildContextState(), dispatch }}
        >
          <DateTime
            content={{ type: "input_date_time" as any, properties }}
            mode={UserFormModeTypes.EDIT}
            onChange={jest.fn()}
            withConfirmationDialog={true}
            reportDate={true}
          />
        </CustomisedFromStateContext.Provider>
      </ToastProvider>
    );

    // Expect dispatch to be called at least once with CHANGE_INITIAL_STATE on mount
    expect(dispatch).toHaveBeenCalledWith(
      expect.objectContaining({
        type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
        payload: expect.objectContaining({
          properties: expect.objectContaining({
            report_start_date: "2024-03-15",
          }),
        }),
      })
    );
  });

  it("3) updates properties.user_value in parent on every change (including initial auto-populate and manual)", () => {
    // First render with startDate triggers initial auto-populate
    (useRouter as jest.Mock).mockReturnValue({
      query: { startDate: "2024-04-20" },
    });

    function Parent() {
      const [userValue, setUserValue] = useState<any>(null);
      const dispatch = jest.fn();

      const properties = {
        title: "Report Date",
        is_mandatory: false,
        comments_allowed: false,
        attachments_allowed: false,
        selected_type: "date_only" as const,
        date_response_type: "auto_populate_current_date" as const,
        date_options: "single_date" as const,
        date_type: "single_date" as const,
        user_value: userValue,
        user_comments: null,
        user_attachments: null,
      } as any;

      return (
        <ToastProvider>
          <CustomisedFromStateContext.Provider
            value={{ state: buildContextState(), dispatch }}
          >
            <DateTime
              content={{ type: "input_date_time" as any, properties }}
              mode={UserFormModeTypes.EDIT}
              onChange={val => setUserValue(val)}
              withConfirmationDialog={false}
              reportDate={false}
            />
            <div data-testid="userValue">{userValue?.value || ""}</div>
          </CustomisedFromStateContext.Provider>
        </ToastProvider>
      );
    }

    render(<Parent />);

    // After mount, initial auto-populate should set parent's user_value to startDate
    expect(screen.getByTestId("userValue").textContent).toBe("2024-04-20");

    // Now simulate manual change
    const inputs = screen.getAllByDisplayValue("2024-04-20");
    const targetInput = inputs.find(input => input.id === "Report Date") as HTMLInputElement;
    fireEvent.change(targetInput, { target: { value: "2024-04-22" } });

    // Parent's user_value should reflect the new change
    expect(screen.getByTestId("userValue").textContent).toBe("2024-04-22");
  });

  it("4) updates report_start_date on save and continue when reportDate is true", () => {
    const dispatch = jest.fn();
    (useRouter as jest.Mock).mockReturnValue({ query: {} });

    const properties = {
      title: "Report Date",
      is_mandatory: false,
      comments_allowed: false,
      attachments_allowed: false,
      selected_type: "date_only" as const,
      date_response_type: "calendar" as const,
      date_options: "single_date" as const,
      date_type: "single_date" as const,
      user_value: { value: "2025-01-15" },
      user_comments: null,
      user_attachments: null,
    } as any;

    render(
      <ToastProvider>
        <CustomisedFromStateContext.Provider
          value={{ state: buildContextState(), dispatch }}
        >
          <DateTime
            content={{ type: "input_date_time" as any, properties }}
            mode={UserFormModeTypes.EDIT}
            onChange={jest.fn()}
            withConfirmationDialog={false}
            reportDate={true}
          />
        </CustomisedFromStateContext.Provider>
      </ToastProvider>
    );

    // Simulate save and continue event
    formEventEmitter.emit(FORM_EVENTS.SAVE_AND_CONTINUE);

    // Verify that dispatch was called with updated report_start_date
    expect(dispatch).toHaveBeenCalledWith(
      expect.objectContaining({
        type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
        payload: expect.objectContaining({
          properties: expect.objectContaining({
            report_start_date: "2025-01-15",
          }),
        }),
      })
    );
  });

  it("5) updates report_start_date on save and continue with startDate from router when available", () => {
    const dispatch = jest.fn();
    (useRouter as jest.Mock).mockReturnValue({
      query: { startDate: "2024-03-15" },
    });

    const properties = {
      title: "Report Date",
      is_mandatory: false,
      comments_allowed: false,
      attachments_allowed: false,
      selected_type: "date_only" as const,
      date_response_type: "calendar" as const,
      date_options: "single_date" as const,
      date_type: "single_date" as const,
      user_value: null, // Set to null so startDate from router will be used
      user_comments: null,
      user_attachments: null,
    } as any;

    render(
      <ToastProvider>
        <CustomisedFromStateContext.Provider
          value={{ state: buildContextState(), dispatch }}
        >
          <DateTime
            content={{ type: "input_date_time" as any, properties }}
            mode={UserFormModeTypes.EDIT}
            onChange={jest.fn()}
            withConfirmationDialog={false}
            reportDate={true}
          />
        </CustomisedFromStateContext.Provider>
      </ToastProvider>
    );

    // Simulate save and continue event
    formEventEmitter.emit(FORM_EVENTS.SAVE_AND_CONTINUE);

    // Verify that dispatch was called with startDate from router (prioritized over localValue)
    expect(dispatch).toHaveBeenCalledWith(
      expect.objectContaining({
        type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
        payload: expect.objectContaining({
          properties: expect.objectContaining({
            report_start_date: "2024-03-15",
          }),
        }),
      })
    );
  });

  it("6) updates report_start_date on save and continue with localValue when both localValue and startDate exist", () => {
    const dispatch = jest.fn();
    (useRouter as jest.Mock).mockReturnValue({
      query: { startDate: "2024-03-15" },
    });

    const properties = {
      title: "Report Date",
      is_mandatory: false,
      comments_allowed: false,
      attachments_allowed: false,
      selected_type: "date_only" as const,
      date_response_type: "calendar" as const,
      date_options: "single_date" as const,
      date_type: "single_date" as const,
      user_value: { value: "2025-01-15" }, // This should take priority
      user_comments: null,
      user_attachments: null,
    } as any;

    render(
      <ToastProvider>
        <CustomisedFromStateContext.Provider
          value={{ state: buildContextState(), dispatch }}
        >
          <DateTime
            content={{ type: "input_date_time" as any, properties }}
            mode={UserFormModeTypes.EDIT}
            onChange={jest.fn()}
            withConfirmationDialog={false}
            reportDate={true}
          />
        </CustomisedFromStateContext.Provider>
      </ToastProvider>
    );

    // Simulate save and continue event
    formEventEmitter.emit(FORM_EVENTS.SAVE_AND_CONTINUE);

    // Verify that dispatch was called with localValue (prioritized over startDate from router)
    expect(dispatch).toHaveBeenCalledWith(
      expect.objectContaining({
        type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
        payload: expect.objectContaining({
          properties: expect.objectContaining({
            report_start_date: "2025-01-15",
          }),
        }),
      })
    );
  });
});
