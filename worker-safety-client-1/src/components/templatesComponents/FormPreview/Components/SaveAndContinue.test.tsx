/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/no-var-requires */
import { render } from "@testing-library/react";
import router from "next/router";
import {
  formEventEmitter,
  FORM_EVENTS,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import SaveAndContinue from "./SaveAndContinue";

// Mock dependencies
jest.mock("next/router", () => ({
  push: jest.fn(),
  query: {},
}));

jest.mock(
  "@/context/CustomisedDataContext/CustomisedFormStateProvider",
  () => ({
    formEventEmitter: {
      addListener: jest.fn(),
      emit: jest.fn(),
    },
    FORM_EVENTS: {
      SAVE_AND_CONTINUE: "SAVE_AND_CONTINUE",
    },
  })
);

jest.mock("@/api/customFlowApi");
jest.mock("@/hooks/useRestMutation", () => () => ({
  mutate: jest.fn(),
  isLoading: false,
  error: null,
  responseData: null,
}));
jest.mock("@/hooks/useCWFFormState", () => () => ({
  setCWFFormStateDirty: jest.fn(),
}));
jest.mock("./FormRendererContext", () => ({
  useFormRendererContext: () => ({
    hasRecommendedHazards: false,
    selectedHazards: [],
    isHazardsAndControlsPage: false,
    setShowMissingControlsError: jest.fn(),
    manuallyAddHazardsHandler: jest.fn(),
  }),
}));

// Mock React context
const mockContextValue = {
  state: {
    form: {
      id: "form123",
      contents: [],
      isDisabled: false,
      component_data: {},
    },
  },
  dispatch: jest.fn(),
};

jest.mock("react", () => ({
  ...jest.requireActual("react"),
  useContext: jest.fn(() => mockContextValue),
  useRef: jest.fn(() => ({ current: false })),
  useState: jest.fn((initial: any) => [initial, jest.fn()]),
  useEffect: jest.fn((fn: () => void) => fn()),
}));

// Mock window.history.replaceState
Object.defineProperty(window, "history", {
  value: {
    replaceState: jest.fn(),
  },
  writable: true,
});

describe("SaveAndContinue - createFormCompleted useEffect", () => {
  const mockProps = {
    activePageDetails: {
      id: "page1",
      parentId: "root",
      type: "page" as any,
    },
    formObject: {
      id: "form123",
      contents: [],
      properties: { status: "in_progress" },
      metadata: {},
      template_id: "template1",
      created_by: { id: "user1" },
      component_data: {},
    } as any,
    setActivePageDetails: jest.fn(),
    onSaveAndContinue: jest.fn(),
    isFirstSave: false,
    creatingForm: false,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (router as any).query = {
      project: "project123",
      location: "location456",
      startDate: "2023-01-01",
    };
  });

  describe("when createFormCompleted event is emitted", () => {
    let eventCallback: (newFormId?: string) => void;

    beforeEach(() => {
      (formEventEmitter.addListener as any).mockImplementation(
        (event: string, callback: (newFormId?: string) => void) => {
          if (event === "createFormCompleted") {
            eventCallback = callback;
          }
          return { remove: jest.fn() };
        }
      );

      render(<SaveAndContinue {...mockProps} />);
    });

    describe("when isFormSubmisionModalActionTaken.current is true", () => {
      beforeEach(() => {
        const React = require("react");
        React.useRef.mockReturnValue({ current: true });
      });

      it("should navigate to projects page when project exists", () => {
        eventCallback("newForm456");

        expect(router.push).toHaveBeenCalledWith(
          "/projects/project123?location=location456&startDate=2023-01-01"
        );
      });

      it("should navigate to template-forms view when no project", () => {
        (router as any).query = {};

        eventCallback("newForm456");

        expect(router.push).toHaveBeenCalledWith(
          "/template-forms/view?formId=newForm456"
        );
      });

      it("should use state.form.id when newFormId is not provided", () => {
        (router as any).query = {};

        eventCallback();

        expect(router.push).toHaveBeenCalledWith(
          "/template-forms/view?formId=form123"
        );
      });
    });

    describe("when isFormSubmisionModalActionTaken.current is false", () => {
      beforeEach(() => {
        const React = require("react");
        React.useRef.mockReturnValue({ current: false });
      });

      it("should update URL history when creatingForm is true and has project", () => {
        const propsWithCreatingForm = {
          ...mockProps,
          creatingForm: true,
        };

        render(<SaveAndContinue {...propsWithCreatingForm} />);

        eventCallback("newForm456");

        expect(window.history.replaceState).toHaveBeenCalledWith(
          null,
          "",
          "/template-forms/view?formId=newForm456&project=project123&location=location456&startDate=2023-01-01"
        );
      });

      it("should update URL history when creatingForm is true and no project", () => {
        (router as any).query = {};
        const propsWithCreatingForm = {
          ...mockProps,
          creatingForm: true,
        };

        render(<SaveAndContinue {...propsWithCreatingForm} />);

        eventCallback("newForm456");

        expect(window.history.replaceState).toHaveBeenCalledWith(
          null,
          "",
          "/template-forms/view?formId=newForm456"
        );
      });

      it("should not update URL history when creatingForm is false", () => {
        eventCallback("newForm456");

        expect(window.history.replaceState).not.toHaveBeenCalled();
      });

      it("should emit SAVE_AND_CONTINUE event", () => {
        eventCallback("newForm456");

        expect(formEventEmitter.emit).toHaveBeenCalledWith(
          FORM_EVENTS.SAVE_AND_CONTINUE
        );
      });

      it("should emit formUpdated event after timeout", (done: () => void) => {
        eventCallback("newForm456");

        setTimeout(() => {
          expect(formEventEmitter.emit).toHaveBeenCalledWith("formUpdated");
          done();
        }, 10);
      });
    });

    describe("edge cases", () => {
      it("should handle when formId is undefined", () => {
        (router as any).query = {};
        const mockContextWithoutFormId = {
          ...mockContextValue,
          state: {
            ...mockContextValue.state,
            form: {
              ...mockContextValue.state.form,
              id: undefined,
            },
          },
        };

        const React = require("react");
        React.useContext.mockReturnValue(mockContextWithoutFormId);
        React.useRef.mockReturnValue({ current: true });

        render(<SaveAndContinue {...mockProps} />);

        eventCallback();

        expect(router.push).toHaveBeenCalledWith(
          "/template-forms/view?formId=form123"
        );
      });
    });
  });

  describe("cleanup", () => {
    it("should remove event listener on unmount", () => {
      const mockRemove = jest.fn();
      (formEventEmitter.addListener as any).mockReturnValue({
        remove: mockRemove,
      });

      const { unmount } = render(<SaveAndContinue {...mockProps} />);

      unmount();

      expect(mockRemove).toHaveBeenCalled();
    });
  });
});
