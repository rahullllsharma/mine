import type { TaskHazardAggregator } from "@/types/project/HazardAggregator";
import type { TaskAnalysisInputs } from "@/types/report/DailyReportInputs";
import { act, fireEvent, screen } from "@testing-library/react";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { TaskStatus } from "@/types/task/TaskStatus";
import { formRender, mockTenantStore } from "@/utils/dev/jest";
import TaskReportCard from "./TaskReportCard";

const task: TaskHazardAggregator = {
  id: "1",
  name: "Pipe Face Alignment",
  activity: {
    id: "activity1",
    name: "activity1",
    startDate: "2021-10-10",
    endDate: "2021-10-11",
    status: TaskStatus.NOT_STARTED,
    taskCount: 1,
    tasks: [],
  },
  riskLevel: RiskLevel.MEDIUM,
  hazards: [
    {
      id: "1",
      name: "Pinch Point",
      isApplicable: true,
      controls: [
        { id: "1", name: "Gloves", isApplicable: true },
        { id: "2", name: "Situational Jobsite Awareness", isApplicable: false },
      ],
    },
    {
      id: "2",
      name: "Struck by Equipment and Material",
      isApplicable: true,
      controls: [
        { id: "3", name: "Gloves", isApplicable: true },
        { id: "4", name: "Situational Jobsite Awareness", isApplicable: false },
      ],
    },
  ],
  incidents: [],
};

const taskWithImplementedControls: TaskAnalysisInputs = {
  id: "",
  notes: "",
  performed: true,
  hazards: [
    {
      ...task.hazards[0],
      controls: [
        {
          id: "1",
          implemented: true,
        },
        {
          id: "2",
          implemented: true,
        },
      ],
    },
  ],
};

describe(TaskReportCard.name, () => {
  mockTenantStore();
  it('should display the switch button with "Performed" text', () => {
    formRender(<TaskReportCard task={task} />);
    const switchElement = screen.getByRole("switch", { name: /performed/i });
    expect(switchElement.textContent).toBe("Performed");
  });

  it("should display a Text Area", () => {
    formRender(<TaskReportCard task={task} />);
    const textElement = screen.getByRole("textbox");
    expect(textElement).toBeInTheDocument();
  });

  describe("when has a selected task", () => {
    it("should render a note if has a stored note", () => {
      const selectedTask = {
        id: task.id,
        performed: false,
        notes: "hello from note",
        hazards: [],
      } as unknown as TaskAnalysisInputs;

      formRender(<TaskReportCard task={task} selectedTask={selectedTask} />);
      screen.getByText(/hello from note/i);
    });
  });

  describe('when "Mark all controls as implemented" is unchecked', () => {
    it('should render a "Mark all controls as implemented" checkbox', () => {
      formRender(<TaskReportCard task={task} />);
      screen.getByRole("checkbox", {
        name: /mark all controls as implemented/i,
      });
    });

    it('should have at least one control as "not implemented"', () => {
      formRender(<TaskReportCard task={task} />);
      screen.getAllByRole("radio", { checked: false });
    });

    describe.skip('when "Mark all controls as implemented" is clicked', () => {
      it("should set all the controls as implemented", () => {
        act(() => {
          formRender(<TaskReportCard task={task} />);
          fireEvent.click(
            screen.getByRole("checkbox", {
              name: /mark all controls as implemented/i,
              checked: false,
            })
          );
        });

        act(() => {
          screen.getByRole("checkbox", {
            name: /mark all controls as implemented/i,
            checked: true,
          });
        });

        const elements = screen.getAllByRole("radio", {
          name: /implemented/i,
          checked: true,
        });

        const totalControls = task.hazards.reduce(
          (acc, hazard) => acc + hazard.controls.length,
          0
        );
        expect(elements).toHaveLength(totalControls);
      });
    });
  });

  describe.skip('when "Mark all controls as implemented" is checked', () => {
    beforeEach(() => {
      act(() => {
        formRender(
          <TaskReportCard
            task={task}
            selectedTask={taskWithImplementedControls}
          />
        );
      });

      act(() => {
        fireEvent.click(
          screen.getByRole("checkbox", {
            name: /mark all controls as implemented/i,
            checked: true,
          })
        );
      });
    });

    describe("when clicked to uncheck", () => {
      it.todo("should set all the controls as not selected");
    });

    describe('when one control is manually changed to "not implemented"', () => {
      it.todo('should set the "Mark all controls as implemented" as unchecked');
    });
  });

  describe("when all controls are already set as implemented", () => {
    it('should set as checked "Mark all controls as implemented"', () => {
      formRender(
        <TaskReportCard
          task={task}
          selectedTask={taskWithImplementedControls}
        />
      );

      screen.getByRole("checkbox", {
        name: /mark all controls as implemented/i,
        checked: true,
      });
    });
  });
});
