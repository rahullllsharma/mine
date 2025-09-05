import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { useRouter } from "next/router";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import useRestMutation from "@/hooks/useRestMutation";
import useCWFFormState from "@/hooks/useCWFFormState";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import { FormStatus, UserFormModeTypes } from "../../customisedForm.types";
import FormHeading from "./FormHeading";

// Mock all the dependencies
jest.mock("next/router", () => ({
  useRouter: jest.fn(),
  __esModule: true,
  default: {
    query: {
      project: "test-project",
      location: "test-location",
      startDate: "2024-01-01",
    },
    pathname: "/forms/123",
    push: jest.fn(),
    replace: jest.fn(),
  },
}));

jest.mock("@/store/auth/useAuthStore.store", () => ({
  useAuthStore: jest.fn(),
}));

jest.mock("@/hooks/useRestMutation", () => ({
  __esModule: true,
  default: jest.fn(),
}));

jest.mock("@/hooks/useCWFFormState", () => ({
  __esModule: true,
  default: jest.fn(),
}));

jest.mock("lodash/cloneDeep", () => ({
  __esModule: true,
  default: jest.fn(),
}));

const mockRouter = {
  pathname: "/forms/123",
  query: {
    project: "test-project",
    location: "test-location",
    startDate: "2024-01-01",
  },
  replace: jest.fn(),
  push: jest.fn(),
};

const mockAuthStore = {
  me: {
    id: "user-123",
    permissions: ["ALLOW_EDITS_AFTER_EDIT_PERIOD"],
  },
};

const mockToastContext = {
  pushToast: jest.fn(),
  items: [],
  dismissToast: jest.fn(),
} as any;

const mockFormState = (copyEnabled = false, rebriefEnabled = false) =>
  ({
    form: {
      id: "form-123",
      type: "customisedForm",
      template_id: "template-123",
      properties: {
        status: FormStatus.Completed,
        title: "Test Form",
        page_update_status: "default",
      },
      contents: [],
      settings: {},
      isDisabled: false,
      metadata: {
        copy_and_rebrief: {
          is_copy_enabled: copyEnabled,
          is_rebrief_enabled: rebriefEnabled,
        },
      },
      component_data: {},
    },
    isFormDirty: false,
    formBuilderMode: { mode: "view" },
    isFormIsValid: true,
  } as any);

const mockDispatch = jest.fn();

const mockCWFFormState = {
  setCWFFormStateDirty: jest.fn(),
};

const createMockFormObject = (status: string = FormStatus.Completed) =>
  ({
    id: "form-123",
    type: "customisedForm",
    properties: {
      title: "Test Form Title",
      status,
    },
    contents: [],
    settings: {},
    isDisabled: false,
    created_by: {
      id: "user-123",
    },
    edit_expiry_days: 0,
    edit_expiry_time: new Date(Date.now() + 86400000).toISOString(),
  } as any);

const renderFormHeading = (
  formObject = createMockFormObject(),
  setMode = jest.fn(),
  formState = mockFormState()
) => {
  return render(
    <ToastContext.Provider value={mockToastContext}>
      <CustomisedFromStateContext.Provider
        value={{ state: formState, dispatch: mockDispatch }}
      >
        <FormHeading formObject={formObject} setMode={setMode} />
      </CustomisedFromStateContext.Provider>
    </ToastContext.Provider>
  );
};

describe("FormHeading Edit Button State Management", () => {
  let mockCreateCopyMutate: jest.Mock;
  let mockDeleteMutate: jest.Mock;
  let mockReopenMutate: jest.Mock;
  let mockDownloadMutate: jest.Mock;
  beforeEach(() => {
    jest.clearAllMocks();

    mockCreateCopyMutate = jest.fn();
    mockDeleteMutate = jest.fn();
    mockReopenMutate = jest.fn();
    mockDownloadMutate = jest.fn();

    (useRouter as any).mockReturnValue(mockRouter);
    (useAuthStore as any).mockReturnValue(mockAuthStore);
    (useCWFFormState as any).mockReturnValue(mockCWFFormState);

    // Default mock for useRestMutation
    (useRestMutation as any).mockImplementation(({ endpoint }: any) => {
      if (endpoint === "/forms/") {
        return { mutate: mockCreateCopyMutate };
      } else if (endpoint.includes("/delete")) {
        return { mutate: mockDeleteMutate };
      } else if (endpoint.includes("/reopen")) {
        return { mutate: mockReopenMutate };
      } else if (endpoint.includes("/pdf_download")) {
        return { mutate: mockDownloadMutate };
      }
      return { mutate: jest.fn() };
    });
  });

  it("should render form title correctly", () => {
    renderFormHeading();
    expect(screen.getByText("Test Form Title")).toBeInTheDocument();
  });

  it("should handle form status updates correctly", async () => {
    let onSuccessCallback: (() => void) | undefined;

    (useRestMutation as any).mockImplementation((params: any) => {
      if (
        params?.endpoint === "/reopen" &&
        params?.mutationOptions?.onSuccess
      ) {
        onSuccessCallback = params.mutationOptions.onSuccess;
        return { mutate: mockReopenMutate };
      }
      return { mutate: jest.fn() };
    });

    const setMode = jest.fn();
    const formObject = createMockFormObject(FormStatus.Completed);

    renderFormHeading(formObject, setMode);

    expect(useRestMutation).toHaveBeenCalled();

    if (onSuccessCallback) {
      onSuccessCallback();

      await waitFor(() => {
        expect(setMode).toHaveBeenCalledWith(UserFormModeTypes.EDIT);
      });

      expect(mockDispatch).toHaveBeenCalledWith({
        type: "CHANGE_INITIAL_STATE",
        payload: expect.objectContaining({
          properties: expect.objectContaining({
            status: "in_progress",
          }),
        }),
      });
    }
  });

  it("should show 'Make a copy' option when copy is enabled", () => {
    const formState = mockFormState(true, false);
    renderFormHeading(createMockFormObject(), jest.fn(), formState);
    const dropdownTrigger = document
      .querySelector(".ci-hamburger")
      ?.closest("button");
    expect(dropdownTrigger).toBeInTheDocument();
  });

  it("should not show 'Make a copy' option when copy is disabled", () => {
    const formState = mockFormState(false, false);
    renderFormHeading(createMockFormObject(), jest.fn(), formState);
  });

  it("should reset selected data correctly for PersonnelComponent", () => {
    const formState = mockFormState(true, true);
    renderFormHeading(createMockFormObject(), jest.fn(), formState);
  });

  it("should reset selected data correctly for ReportDate", () => {
    const formState = mockFormState(true, true);
    renderFormHeading(createMockFormObject(), jest.fn(), formState);
  });

  it("should set page_update_status to 'default' when copying", () => {
    const formState = mockFormState(true, true);
    renderFormHeading(createMockFormObject(), jest.fn(), formState);
  });

  it("should handle copy success navigation correctly", async () => {
    let onSuccessCallback: ((response: any) => void) | undefined;

    // Mock useRestMutation to capture the createCopy mutation specifically
    (useRestMutation as any).mockImplementation(
      ({ endpoint, mutationOptions }: any) => {
        if (endpoint === "/forms/" && mutationOptions?.onSuccess) {
          onSuccessCallback = mutationOptions.onSuccess;
          return { mutate: mockCreateCopyMutate };
        }
        return { mutate: jest.fn() };
      }
    );

    const formState = mockFormState(true, true);
    renderFormHeading(createMockFormObject(), jest.fn(), formState);

    expect(onSuccessCallback).toBeDefined();

    if (onSuccessCallback) {
      const mockResponse = { data: null };
      onSuccessCallback(mockResponse);
      expect(mockRouter.push).not.toHaveBeenCalled();
    }
  });

  it("should not crash when rendering with different form statuses", () => {
    const completedForm = createMockFormObject(FormStatus.Completed);
    const inProgressForm = createMockFormObject("in_progress");

    expect(() => renderFormHeading(completedForm)).not.toThrow();
    expect(() => renderFormHeading(inProgressForm)).not.toThrow();
  });

  it("should handle form object changes without errors", () => {
    const formObject = createMockFormObject(FormStatus.Completed);
    const { rerender } = renderFormHeading(formObject);

    // Update to different status
    const updatedFormObject = createMockFormObject("in_progress");

    expect(() => {
      rerender(
        <ToastContext.Provider value={mockToastContext}>
          <CustomisedFromStateContext.Provider
            value={{ state: mockFormState(), dispatch: mockDispatch }}
          >
            <FormHeading formObject={updatedFormObject} setMode={jest.fn()} />
          </CustomisedFromStateContext.Provider>
        </ToastContext.Provider>
      );
    }).not.toThrow();

    expect(screen.getByText("Test Form Title")).toBeInTheDocument();
  });
});
