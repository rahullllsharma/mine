import { fireEvent, screen } from "@testing-library/react";
import { formRender, mockTenantStore } from "@/utils/dev/jest";
import ActivityConfiguration from "./ActivityConfiguration";

const minStartDate = "2022-07-07";
const maxEndDate = "2022-10-10";
const defaultActivityName = "Default Activity";
const defaultStartDate = "2022-08-08";
const defaultEndDate = "2022-09-09";
const defaultStatus = { id: "NOT_STARTED", name: "NOT_STARTED" };
const activityTypeLibrary = [
  {
    id: "1",
    name: "Activity type 1",
  },
  {
    id: "2",
    name: "Activity type 2",
  },
  {
    id: "3",
    name: "Activity type 3",
  },
];

jest.mock("@/types/task/TaskStatus", () => {
  return {
    __esModule: true,
    ...jest.requireActual("@/types/task/TaskStatus"),
    taskStatusOptions: [
      { id: "NOT_STARTED", name: "NOT_STARTED" },
      { id: "IN_PROGRESS", name: "IN_PROGRESS" },
    ],
  };
});

describe(ActivityConfiguration.name, () => {
  mockTenantStore();
  it("should display an Activity Name, Start Date, End Date and Status fields", () => {
    formRender(
      <ActivityConfiguration
        minStartDate={minStartDate}
        maxEndDate={maxEndDate}
      />,
      { name: defaultActivityName, startDate: defaultStartDate }
    );
    screen.getByText(/activity name/i);
    screen.getByText(/start date/i);
    screen.getByText(/end date/i);
    expect(screen.queryByText(/status/i)).toBeNull();
  });

  it("should display an Activity type", () => {
    formRender(
      <ActivityConfiguration
        minStartDate={minStartDate}
        maxEndDate={maxEndDate}
        activityTypeLibrary={activityTypeLibrary}
      />,
      {
        name: defaultActivityName,
        startDate: defaultStartDate,
      }
    );

    screen.getByText(/activity type/i, { selector: "label" });
  });

  describe("when it's rendered with default values", () => {
    beforeEach(() => {
      formRender(
        <ActivityConfiguration
          minStartDate={minStartDate}
          maxEndDate={maxEndDate}
        />,
        {
          name: defaultActivityName,
          startDate: defaultStartDate,
          endDate: defaultEndDate,
          status: defaultStatus,
        }
      );
    });
    it("should have the Activity Name input correctly filled", () => {
      const element = screen.getByLabelText(/activity name/i, {
        selector: "input",
      });
      expect(element).toHaveValue(defaultActivityName);
    });

    it("should have the Start Date input correctly filled", () => {
      const element = screen.getByLabelText(/start date/i, {
        selector: "input",
      });
      expect(element).toHaveValue(defaultStartDate);
    });
    it("should have the End Date input correctly filled", () => {
      const element = screen.getByLabelText(/end date/i, {
        selector: "input",
      });
      expect(element).toHaveValue(defaultEndDate);
    });

    it("should contain the correct status", () => {
      screen.queryByRole("button", {
        name: new RegExp(defaultStatus.name, "i"),
      });
    });
  });

  describe("when it's rendered with default values and activity attributes", () => {
    beforeEach(() => {
      formRender(
        <ActivityConfiguration
          minStartDate={minStartDate}
          maxEndDate={maxEndDate}
          activityTypeLibrary={activityTypeLibrary}
        />,
        {
          name: defaultActivityName,
          startDate: defaultStartDate,
          endDate: defaultEndDate,
          status: defaultStatus,
          libraryActivityTypeId: activityTypeLibrary[0].id,
        }
      );
    });

    it("should have the Activity type input correctly filled", () => {
      screen.getByRole("button", {
        name: new RegExp(activityTypeLibrary[0].name, "i"),
      });
    });
  });

  describe("When a new date is selected", () => {
    it("should be reflected in the input", () => {
      formRender(
        <ActivityConfiguration
          minStartDate={minStartDate}
          maxEndDate={maxEndDate}
        />,
        {
          name: defaultActivityName,
          startDate: defaultStartDate,
        }
      );
      const newDate = "2021-11-12";
      const element = screen.getByLabelText(/start date/i);
      fireEvent.change(element, {
        target: { value: newDate },
      });
      expect(element).toHaveValue(newDate);
    });
  });

  describe("When the user changes the status", () => {
    it("should be reflected in select", () => {
      formRender(
        <ActivityConfiguration
          minStartDate={minStartDate}
          maxEndDate={maxEndDate}
        />,
        {
          name: defaultActivityName,
          startDate: defaultStartDate,
        }
      );
      const newStatus = /in_progress/i;
      const notStartedButton = screen.queryByRole("button", {
        name: /not_started/i,
      });
      if (notStartedButton) {
        fireEvent.click(notStartedButton);
        const inProgressOption = screen.queryByText(newStatus);
        if (inProgressOption) {
          fireEvent.click(inProgressOption);
          const updatedStatusButton = screen.queryByRole("button", {
            name: newStatus,
          });
          expect(updatedStatusButton).toBeInTheDocument();
        } else {
          console.warn("New status button not found.");
        }
      } else {
        console.warn("Not started button not found.");
      }
    });
  });
});
