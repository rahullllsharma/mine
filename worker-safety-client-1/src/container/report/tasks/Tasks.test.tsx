import type { TasksProps } from "./Tasks";
import { screen, fireEvent, within } from "@testing-library/react";

import { useProjects } from "@/hooks/useProjects";
import { transformTasksToListTasks } from "@/utils/task";

import { formRender, mockTenantStore } from "@/utils/dev/jest";
import Tasks from "./Tasks";

// eslint-disable-next-line react-hooks/rules-of-hooks
const { tasks } = useProjects()[0].locations[0];
const projectTasks = transformTasksToListTasks(tasks);

describe(Tasks.name, () => {
  mockTenantStore();
  it("should render the titles", () => {
    const { asFragment } = formRender(<Tasks tasks={projectTasks} />);

    screen.getByRole("heading", { level: 3 });
    screen.getByText(
      "Select the tasks you were responsible for overseeing at this location."
    );

    expect(asFragment()).toMatchSnapshot();
  });

  it("should render with the default selections", () => {
    formRender(
      <Tasks
        tasks={projectTasks.map(task => ({
          ...task,
          isSelected: false,
        }))}
      />
    );

    screen.getAllByRole("listitem").forEach(item => {
      expect(within(item).getByRole("checkbox")).not.toBeChecked();
    });
  });

  it.each([false, undefined, null, []] as TasksProps["tasks"][])(
    "should render the empty state when no tasks are found",
    taskListItem => {
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      formRender(<Tasks tasks={taskListItem} />);
      screen.getByText(
        "There are currently no activities in progress between the set contractor start and end dates."
      );
    }
  );

  describe("when has tasks", () => {
    it("should have the all tasks checkbox checked if all tasks are selected", () => {
      const allSelectedTasks = transformTasksToListTasks(tasks, tasks);
      formRender(<Tasks tasks={allSelectedTasks} />);

      expect(
        screen.getByRole("checkbox", {
          name: /all tasks/i,
        })
      ).toBeChecked();
    });

    it("should have the all tasks checkbox unchecked if one of tasks is NOT selected", () => {
      const projectsWithUnselected = projectTasks.concat();
      projectsWithUnselected[0].isSelected = false;

      formRender(<Tasks tasks={projectsWithUnselected} />);

      expect(
        screen.getByRole("checkbox", {
          name: /all tasks/i,
        })
      ).not.toBeChecked();
    });

    describe("for each tasks", () => {
      it("should have be checked/unchecked based if it is selected or not", () => {
        const projectsWithUnselected = projectTasks.concat();
        projectsWithUnselected[0].isSelected = false;

        formRender(<Tasks tasks={projectsWithUnselected} />);

        projectsWithUnselected.forEach(task => {
          expect(
            (
              screen.getByRole("checkbox", {
                name: task.name,
              }) as HTMLInputElement
            ).checked
          ).toBe(task.isSelected);
        });
      });
    });

    describe("when clicking the 'All Tasks' checkbox", () => {
      it.each(["on", "off"])(
        "and the checkbox is %s, should change all task checkboxes with the opposite value",
        value => {
          const isSelected = value === "on";
          formRender(
            <Tasks
              tasks={projectTasks.map(task => ({ ...task, isSelected }))}
            />
          );

          fireEvent.click(screen.getByRole("checkbox", { name: /all tasks/i }));

          // since we trigger the All Tasks checkbox,
          // we query if NO checkbox has the initial value
          expect(
            screen.queryAllByRole("checkbox", { checked: isSelected })
          ).toHaveLength(0);
        }
      );
    });

    describe("when clicking a task", () => {
      it.each(["on", "off"])(
        "and the task is %s, should change that task with the opposite value",
        value => {
          const isSelected = value === "on";

          const selected = projectTasks[1];
          const taskListItem = projectTasks.map(task => ({
            ...task,
            isSelected: task.id === selected.id ? isSelected : task.isSelected,
          }));

          formRender(<Tasks tasks={taskListItem} />);

          fireEvent.click(
            screen.getByRole("checkbox", { name: selected.name })
          );

          screen.queryByRole("checkbox", {
            name: selected.name,
            checked: !isSelected,
          });
        }
      );
    });
  });
});
