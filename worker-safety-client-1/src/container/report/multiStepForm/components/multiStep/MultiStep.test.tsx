import {
  act,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import AdditionalInformation from "@/container/report/additionalInformation/AdditionalInformation";
import WorkSchedule from "@/container/report/workSchedule/WorkSchedule";
import { formRender, mockTenantStore } from "@/utils/dev/jest";
import * as hook from "../../hooks/useMultiStep";
import MultiStepWithForm from "./MultiStep";

const defaults = {
  startDate: "2022-01-05T10:10",
  endDate: "2022-01-29T10:10",
  dateLimits: {
    projectStartDate: "2022-01-01T00:00",
    projectEndDate: "2022-01-31T23:59",
  },
};

const form = {
  additionalInformation: {
    lessons: "hello world",
  },
};

const bootInitialProps = () => ({
  ...defaults,
  form,
});

const steps = [
  {
    id: "workSchedule",
    name: "workSchedule",
    path: "#workSchedule",
    Component: function WorkScheduleSection(props: any) {
      return (
        <WorkSchedule
          startDate="2022-01-01"
          endDate="2022-01-31"
          dateLimits={{
            projectEndDate: "2022-01-31",
            projectStartDate: "2022-01-01",
          }}
          {...props}
        />
      );
    },
  },
  {
    id: "additionalInformation",
    name: "additionalInformation",
    path: "#additionalInformation",
    Component: function AdditionalInformationSection() {
      return <AdditionalInformation />;
    },
  },
];

jest.mock("../../hooks/useMultiStep", () => ({
  useMultiStepState: jest.fn(() => ({
    isCompleted: false,
    current: steps[0],
    steps,
  })),
  useMultiStepActions: jest.fn(() => ({
    moveForward: jest.fn(),
    moveBack: jest.fn(),
    moveForwardAndComplete: jest.fn(),
    markCurrentAs: jest.fn(),
  })),
}));

describe(MultiStepWithForm.name, () => {
  mockTenantStore();
  let cacheHistoryState: History;

  beforeAll(() => {
    cacheHistoryState = window.history;

    Object.defineProperty(window, "history", {
      value: {
        replaceState: jest.fn(),
        state: {
          as: "pathname",
        },
      },
      writable: true,
    });

    window.HTMLElement.prototype.scrollTo = jest.fn();
    window.HTMLElement.prototype.scrollIntoView = jest.fn();
  });

  afterAll(() => {
    Object.defineProperties(
      window.history,
      cacheHistoryState as unknown as PropertyDescriptorMap
    );
  });

  it("should render the current step", async () => {
    /**
     * Avoid the following issue:
     * When testing, code that causes React state updates should be wrapped into act(...):
     * act(() => { / * fire events that update state * /});
     * // assert on the output
     **/
    act(() => {
      formRender(<MultiStepWithForm />);
    });

    // non-mobile navigation
    expect(
      screen.getByRole("tab", { name: /workschedule/i })
    ).toBeInTheDocument();
    // mobile-only navigation
    expect(
      screen.getByRole("button", { name: /workschedule/i })
    ).toBeInTheDocument();
  });

  it("should render a navigation for both mobile and desktop", async () => {
    act(() => {
      formRender(<MultiStepWithForm />);
    });

    const navigation = screen.getByTestId("multi-step-navigation");
    // non-mobile navigation
    expect(within(navigation).getByRole("tablist")).toBeInTheDocument();
    // mobile-only navigation
    expect(within(navigation).getByTestId("select")).toBeInTheDocument();
  });

  describe("when navigating between sections", () => {
    xit("should dispatch the default values on the first render and then only new values per section", async () => {
      const onStepSaveHandler = jest.fn().mockResolvedValue(true);
      formRender(
        <MultiStepWithForm
          onStepSave={onStepSaveHandler}
          onStepMount={bootInitialProps}
        />
      );

      await screen.findByText(/contractor work start date/gi);
      fireEvent.click(screen.getByText(/save and continue/gi));

      // due to the test and mocks we need to manually move it forward
      (hook.useMultiStepState as jest.Mock).mockReturnValue({
        current: steps[1],
        steps,
      });

      await waitFor(() => Promise.resolve(1));
      // only includes the change per section
      expect(onStepSaveHandler).toHaveBeenCalledWith({
        sectionIsValid: true,
        workSchedule: {
          endDatetime: "2022-01-29T10:10",
          startDatetime: "2022-01-05T10:10",
        },
      });

      // wait until we see the next section
      await screen.findByText(/lessons/gi);

      // due to the test and mocks we need to manually move it forward
      (hook.useMultiStepState as jest.Mock).mockReturnValue({
        current: steps[0],
        steps,
      });

      fireEvent.click(screen.getByText(/save and continue/gi));
      await waitFor(() => Promise.resolve(1));

      expect(onStepSaveHandler).toHaveBeenLastCalledWith({
        sectionIsValid: true,
        additionalInformation: {
          lessons: "hello world",
          progress: undefined,
        },
      });

      await screen.findByText(/contractor work start date/gi);
      fireEvent.click(screen.getByText(/save and continue/gi));

      await waitFor(() => Promise.resolve(1));
      // Pass the section form data for that section + the form but it was reseted
      expect(onStepSaveHandler).toHaveBeenLastCalledWith({
        additionalInformation: {},
        workSchedule: {
          endDatetime: "2022-01-29T10:10",
          startDatetime: "2022-01-05T10:10",
        },
      });
    });
  });

  describe("when clicking the submit button", () => {
    describe("when the form is valid", () => {
      xit("should call the onSaveStep handler with the flag `sectionIsValid` true", async () => {
        const onSaveStepHandler = jest.fn();
        await act(async () => {
          formRender(
            <MultiStepWithForm
              onStepSave={onSaveStepHandler}
              onStepMount={() => ({
                ...defaults,
                startDatetime: "2022-01-05T10:10",
                endDatetime: "2022-01-29T10:20",
              })}
            />
          );

          screen.getByTestId("multi-step-navigation");
          fireEvent.click(screen.getByText(/save and continue/i));
        });

        expect(onSaveStepHandler).toHaveBeenCalledWith({
          sectionIsValid: true,
          workSchedule: {
            ...defaults,
            startDatetime: "2022-01-05T10:10",
            endDatetime: "2022-01-29T10:20",
          },
        });
      });
    });

    describe("when the form is NOT valid", () => {
      xit("should switch the label to saving when submitting the form", async () => {
        const onSaveStepHandlerMocked = function () {
          return new Promise<{ data: any; errors: any }>(r => {
            setTimeout(() => {
              return r({
                data: {},
                errors: {},
              });
            }, 1);
          });
        };

        await act(async () => {
          formRender(
            <MultiStepWithForm onStepSave={onSaveStepHandlerMocked} />
          );
          screen.getByTestId("multi-step-navigation");
          fireEvent.click(screen.getByText(/save and continue/i));
        });

        screen.getByText(/saving/i);
      });

      it("should call the onSaveStep handler with the flag `sectionIsValid` false", async () => {
        const onSaveStepHandlerMocked = jest.fn();
        await act(async () => {
          formRender(
            <MultiStepWithForm onStepSave={onSaveStepHandlerMocked} />
          );
          screen.getByTestId("multi-step-navigation");
          fireEvent.click(screen.getByText(/save and continue/i));
        });

        expect(onSaveStepHandlerMocked).toHaveBeenCalledWith(
          expect.objectContaining({
            sectionIsValid: false,
          })
        );
      });
    });
  });

  describe("when navigating away while has dirty fields in the current section", () => {
    it.todo("should prompt the user if the user wants to navigate away`");
  });

  describe("steps", () => {
    describe("lifecycle events", () => {
      it.todo("should trigger the onStepMount event, when mounting a step");

      it.todo("should trigger the onStepUnmount event, when unmounting a step");

      describe("when navigating between sections (steps)", () => {
        it.todo("should call the onStepChange event");

        describe("when clicking the save button ", () => {
          it.todo("should trigger the onStepSave event");
          it.todo("should move to the next step when has steps available");
          it.todo(
            "should NOT move to the next step when reached the final step"
          );

          describe("when has an issue with the submission", () => {
            it.todo("should display a toast with a warning");
          });
        });

        describe("when has uncompleted inputs", () => {
          it.todo("should prompt user if the user wants to change sections");
        });
        describe("when is completed", () => {
          it.todo("should change between sections");
        });
      });
    });

    describe("when has all steps are completed", () => {
      const onCompletedHandler = jest.fn();
      beforeEach(async () => {
        const onSaveStepHandler = jest.fn();
        await act(async () => {
          render(
            <MultiStepWithForm
              onStepSave={onSaveStepHandler}
              onComplete={onCompletedHandler}
              onStepMount={() => ({
                ...defaults,
                startDatetime: "2022-01-05T10:10",
                endDatetime: "2022-01-29T10:20",
              })}
            />
          );

          screen.getByTestId("multi-step-navigation");
          fireEvent.click(screen.getByText(/save and continue/i));
        });
      });

      it("should change the primary button text to Save and Complete", () => {
        act(async () => {
          expect(
            await screen.findByText(/save and complete/i)
          ).toBeInTheDocument();
        });
      });

      describe("and clicks the save button", () => {
        it("should trigger the onComplete event", async () => {
          act(async () => {
            await screen.findByText(/save and complete/i);
            fireEvent.click(screen.getByText(/save and complete/i));
            expect(onCompletedHandler).toHaveBeenCalled();
          });
        });
      });

      describe("when changes something in the current step", () => {
        it.todo(
          "should change the primary button text back to Save and Continue"
        );
        it.todo("should NOT trigger the onComplete event when clicked");
      });
    });

    describe("when is in read only view", () => {
      it.todo("should hide the primary button");
    });
  });
});
