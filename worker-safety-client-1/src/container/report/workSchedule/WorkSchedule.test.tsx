import { fireEvent, render, screen } from "@testing-library/react";
import { FormProvider, useForm } from "react-hook-form";
import { getFormattedFullDateTime } from "@/utils/date/helper";
import { formRender, formTemplate, mockTenantStore } from "@/utils/dev/jest";
import WorkSchedule, { workScheduleFormInputPrefix } from "./WorkSchedule";

const selectors = Object.freeze({
  ["startDatetime"]: /contractor work start day and time/gi,
  ["endDatetime"]: /contractor work end day and time/gi,
});

const date = "2022-01-09T09:03";
const prevDate = "2022-01-08T10:30";

const startDateTime = "2022-01-01T00:01";
const endDateTime = "2022-01-10T23:59";

const dateLimits = {
  projectStartDate: "2021-12-01T00:00",
  projectEndDate: "2022-02-01T23:59",
};

describe(WorkSchedule.name, () => {
  mockTenantStore();
  const mockOnSubmit = jest.fn();

  const changeValueForSelectorHelper = (selector: RegExp, value?: string) =>
    fireEvent.change(screen.getByLabelText(selector), { target: { value } });

  const TestWrapper = () => {
    const methods = useForm({
      mode: "all",
    });

    return (
      <FormProvider {...methods}>
        <form
          onSubmit={methods.handleSubmit(mockOnSubmit)}
          data-testid="work-schedule-form"
        >
          <WorkSchedule
            startDatetime={startDateTime}
            endDatetime={endDateTime}
            dateLimits={dateLimits}
          />
        </form>
      </FormProvider>
    );
  };

  beforeEach(() => {
    jest.spyOn(window.console, "error").mockImplementation(() => false);
  });

  afterEach(() => {
    mockOnSubmit.mockClear();
  });

  it("should render correctly", () => {
    const { asFragment } = formRender(
      <WorkSchedule
        startDatetime={startDateTime}
        endDatetime={endDateTime}
        dateLimits={dateLimits}
      />
    );

    screen.getByRole("heading", { name: /daily report details/i });
    expect(screen.getByLabelText(selectors["startDatetime"])).toHaveValue(
      startDateTime
    );
    expect(screen.getByLabelText(selectors["endDatetime"])).toHaveValue(
      endDateTime
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("should render with all the inputs passed, including optional time params", () => {
    formRender(
      <WorkSchedule
        startDatetime={startDateTime}
        endDatetime={endDateTime}
        dateLimits={dateLimits}
      />
    );

    expect(screen.getByLabelText(selectors["startDatetime"])).toHaveValue(
      startDateTime
    );
    expect(screen.getByLabelText(selectors["endDatetime"])).toHaveValue(
      endDateTime
    );
  });

  it("should have ranges for the start and end dates datepickers", () => {
    formRender(
      <WorkSchedule
        startDatetime={startDateTime}
        endDatetime={endDateTime}
        dateLimits={dateLimits}
      />
    );

    expect(screen.getByLabelText(selectors["startDatetime"])).toHaveValue(
      startDateTime
    );
    expect(screen.getByLabelText(selectors["startDatetime"])).toHaveProperty(
      "min",
      dateLimits.projectStartDate
    );
    expect(screen.getByLabelText(selectors["startDatetime"])).toHaveProperty(
      "max",
      dateLimits.projectEndDate
    );
    expect(screen.getByLabelText(selectors["endDatetime"])).toHaveValue(
      endDateTime
    );
    expect(screen.getByLabelText(selectors["endDatetime"])).toHaveProperty(
      "min",
      dateLimits.projectStartDate
    );
    expect(screen.getByLabelText(selectors["endDatetime"])).toHaveProperty(
      "max",
      dateLimits.projectEndDate
    );
  });

  describe("field validations", () => {
    describe.each(Object.entries(selectors))(
      "when the required '%s' field is empty",
      (id, selector) => {
        it("should display `this is a required field` error message", async () => {
          render(<TestWrapper />);

          changeValueForSelectorHelper(selector, "");

          fireEvent.submit(screen.getByTestId("work-schedule-form"));
          expect(await screen.findByLabelText(selector)).toBeInvalid();

          // This is a crappy way to test if the error span is present for each control
          expect(
            document
              .querySelector(`#${workScheduleFormInputPrefix}\\.${id}-err`)
              ?.textContent?.trim()
          ).toEqual("This is a required field");

          expect(mockOnSubmit).not.toHaveBeenCalled();
        });
      }
    );

    describe("when trying a date that is not within the date limits for the project", () => {
      it.each`
        id                 | selectedDate          | label                    | useSameDateForDatePicker
        ${"startDatetime"} | ${"2021-05-01T00:00"} | ${"Start Date and time"} | ${undefined}
        ${"startDatetime"} | ${"2023-01-20T00:00"} | ${"Start Date and time"} | ${"endDatetime"}
        ${"endDatetime"}   | ${"2021-05-01T00:00"} | ${"End Date and time"}   | ${undefined}
        ${"endDatetime"}   | ${"2023-01-20T00:00"} | ${"End Date and time"}   | ${undefined}
      `(
        "should display a error message when $id is used with the out of range date ($date)",
        async ({
          id,
          selectedDate,
          label,
          useSameDateForDatePicker,
        }: {
          id: keyof typeof selectors;
          selectedDate: string;
          label: string;
          useSameDateForDatePicker: keyof typeof selectors;
        }) => {
          const selector = selectors[id];
          render(<TestWrapper />);
          changeValueForSelectorHelper(selectors["endDatetime"], startDateTime);
          changeValueForSelectorHelper(selectors["startDatetime"], endDateTime);

          changeValueForSelectorHelper(selector, selectedDate);

          // Sometimes we need to override the other datepicker to avoid triggering other validation rules.
          if (useSameDateForDatePicker) {
            changeValueForSelectorHelper(
              selectors[useSameDateForDatePicker],
              selectedDate
            );
          }

          fireEvent.submit(screen.getByTestId("work-schedule-form"));

          expect(await screen.findByLabelText(selector)).toBeInvalid();

          // This is a crappy way to test if the error span is present for each control
          expect(
            document
              .querySelector(`#${workScheduleFormInputPrefix}\\.${id}-err`)
              ?.textContent?.trim()
          ).toEqual(
            `Contractor Work ${label} cannot start before ${new Intl.DateTimeFormat(
              undefined,
              {
                dateStyle: "short",
                timeStyle: "short",
              }
            ).format(
              new Date(dateLimits.projectStartDate)
            )} and end after ${new Intl.DateTimeFormat(undefined, {
              dateStyle: "short",
              timeStyle: "short",
            }).format(new Date(dateLimits.projectEndDate))}`
          );

          expect(mockOnSubmit).not.toHaveBeenCalled();
        }
      );
    });

    describe("when Contractor Work Start Date is greater than Contractor Work End Date", () => {
      it("it should update the end date and time and match the start date and time", async () => {
        const selector = selectors["startDatetime"];

        render(<TestWrapper />);

        changeValueForSelectorHelper(selectors["endDatetime"], prevDate);
        changeValueForSelectorHelper(selector, date);

        expect(screen.getByLabelText(selectors["endDatetime"])).toHaveValue(
          date
        );
      });
    });
  });

  it("should submit the validated inputs", async () => {
    render(<TestWrapper />);

    changeValueForSelectorHelper(selectors["endDatetime"], date);
    changeValueForSelectorHelper(selectors["startDatetime"], date);

    fireEvent.submit(screen.getByTestId("work-schedule-form"));

    expect(await screen.findByTestId("work-schedule-form")).toHaveFormValues({
      [`${workScheduleFormInputPrefix}.startDatetime`]: date,
      [`${workScheduleFormInputPrefix}.endDatetime`]: date,
    });

    expect(mockOnSubmit).toHaveBeenCalled();
  });

  it("reopen daily reports keep date input valid", () => {
    // With an complete daily report
    const { rerender } = render(
      formTemplate(
        <WorkSchedule
          startDatetime={startDateTime}
          endDatetime={endDateTime}
          dateLimits={dateLimits}
          isCompleted={true}
        />
      )
    );

    expect(screen.getByLabelText(selectors["startDatetime"])).toHaveValue(
      getFormattedFullDateTime(startDateTime)
    );
    expect(screen.getByLabelText(selectors["endDatetime"])).toHaveValue(
      getFormattedFullDateTime(endDateTime)
    );

    // If we reopen, it should keep input date valid
    rerender(
      formTemplate(
        <WorkSchedule
          startDatetime={startDateTime}
          endDatetime={endDateTime}
          dateLimits={dateLimits}
          isCompleted={false}
        />
      )
    );
    expect(screen.getByLabelText(selectors["startDatetime"])).toHaveValue(
      startDateTime
    );
    expect(screen.getByLabelText(selectors["endDatetime"])).toHaveValue(
      endDateTime
    );
  });
});
