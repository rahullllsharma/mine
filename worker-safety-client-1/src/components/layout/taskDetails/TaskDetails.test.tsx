import type { Hazard } from "@/types/project/Hazard";
import type { Control } from "@/types/project/Control";
import { fireEvent, screen } from "@testing-library/react";
import { formRender, mockTenantStore, openSelectMenu } from "@/utils/dev/jest";
import { TaskStatus } from "@/types/task/TaskStatus";
import { RiskLevel } from "../../riskBadge/RiskLevel";
import { TaskDetails } from "./TaskDetails";

const task = {
  id: "1",
  name: "Task 1",
  riskLevel: RiskLevel.MEDIUM,
  activity: {
    id: "1",
    name: "activity",
    status: TaskStatus.NOT_STARTED,
    startDate: "2022-01-01",
    endDate: "2022-01-03",
    taskCount: 0,
    tasks: [],
  },
  hazards: [
    {
      id: "1",
      name: "hazard 123",
      isApplicable: true,
      controls: [
        {
          id: "1",
          name: "control name",
          isApplicable: true,
        },
        {
          id: "2",
          name: "control name 2",
          isApplicable: true,
        },
      ],
    },
    {
      id: "2",
      name: "hazard 567",
      isApplicable: true,
      controls: [
        {
          id: "12",
          name: "control name",
          isApplicable: true,
        },
        {
          id: "22",
          name: "control name 2",
          isApplicable: true,
        },
      ],
    },
  ],
  incidents: [],
};

// Information should be retrieved by using useQuery and fetched from BE
const controlsLibrary: Control[] = [
  { id: "custom-control-1", name: "Control 1", isApplicable: true },
  { id: "custom-control-2", name: "Control 2", isApplicable: true },
  { id: "custom-control-3", name: "Control 3", isApplicable: true },
  { id: "custom-control-4", name: "Control 4", isApplicable: true },
];

// Information should be retrieved by using useQuery and fetched from BE
const hazardsLibrary: Hazard[] = [
  { id: "custom-hazard-1", name: "Hazard 1", isApplicable: true, controls: [] },
  { id: "custom-hazard-2", name: "Hazard 2", isApplicable: true, controls: [] },
  { id: "custom-hazard-3", name: "Hazard 3", isApplicable: true, controls: [] },
  { id: "custom-hazard-4", name: "Hazard 4", isApplicable: true, controls: [] },
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

describe(TaskDetails.name, () => {
  mockTenantStore();

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe("when is rendered with default values", () => {
    beforeEach(() => {
      formRender(
        <TaskDetails
          task={task}
          hazardsLibrary={hazardsLibrary}
          controlsLibrary={controlsLibrary}
        />,
        {
          status: { id: task.activity.status },
        }
      );
    });

    describe('when the "add hazard" button is clicked', () => {
      beforeEach(() => {
        fireEvent.click(
          screen.getByRole("button", {
            name: /add a hazard/i,
          })
        );
      });

      it("should render the custom hazard select element", () => {
        const selectElement = screen.getByRole("button", {
          name: /select a hazard/i,
        });

        expect(selectElement).toBeInTheDocument();
      });

      it("should be able to select a specific hazard", () => {
        openSelectMenu("button", /select a hazard/i);

        fireEvent.click(
          screen.getByRole("option", {
            name: hazardsLibrary[1].name,
          })
        );

        const selectedElement = screen.getByRole("button", {
          name: new RegExp(hazardsLibrary[1].name, "i"),
        });
        expect(selectedElement).toBeInTheDocument();
      });

      it('should disable the "Add a hazard" button when the number of custom hazards matches the length of the hazards library', () => {
        const buttonElement = screen.getByRole("button", {
          name: /add a hazard/i,
        });
        hazardsLibrary.forEach(() => {
          fireEvent.click(buttonElement);
        });
        expect(buttonElement).toBeDisabled();
      });
    });

    describe('when clicking the "trash" icon in the presence of the custom hazard select element', () => {
      it("should remove the select element", () => {
        fireEvent.click(
          screen.getByRole("button", {
            name: /add a hazard/i,
          })
        );
        fireEvent.click(screen.getByRole("button", { name: /remove/i }));
        expect(screen.queryByText("Select a hazard")).not.toBeInTheDocument();
      });
    });
  });

  describe(`when activity is "${TaskStatus.COMPLETE}"`, () => {
    beforeEach(() => {
      const completedTask = {
        ...task,
        activity: {
          ...task.activity,
          status: TaskStatus.COMPLETE,
        },
      };

      formRender(
        <TaskDetails
          task={completedTask}
          hazardsLibrary={hazardsLibrary}
          controlsLibrary={controlsLibrary}
        />,
        {
          status: { id: task.activity.status },
        }
      );
    });

    it("should not have the 'Add a hazard' button", () => {
      const buttonElement = screen.queryByRole("button", {
        name: /add a hazard/i,
      });

      expect(buttonElement).not.toBeInTheDocument();
    });

    it("should not have the 'Add a control' button", () => {
      const buttonElement = screen.queryByRole("button", {
        name: /add a control/i,
      });

      expect(buttonElement).not.toBeInTheDocument();
    });
  });
});
