import type { LibraryTask } from "@/types/task/LibraryTask";
import { screen, fireEvent, render } from "@testing-library/react";
import { groupBy } from "@/container/Utils";
import { mockTenantStore } from "@/utils/dev/jest";
import ActivityTaskSelection from "./ActivityTaskSelection";

const mockUpdateFilterHandler = jest.fn();

const dummyTasks: LibraryTask[] = [
  {
    id: "task 1",
    name: "Rebar Install",
    category: "Civil Work",
    hazards: [],
    activitiesGroups: [
      {
        id: "aa",
        name: "Civil Work group",
      },
    ],
  },
  {
    id: "task 2",
    name: "Concrete Work",
    category: "Civil Work",
    hazards: [],
    activitiesGroups: [
      {
        id: "aa",
        name: "Civil Work group",
      },
    ],
  },
  {
    id: "task3",
    name: "Clearing",
    category: "Clearing & Grading",
    hazards: [],
    activitiesGroups: [
      {
        id: "cc",
        name: "Clearing",
      },
    ],
  },
];

describe(ActivityTaskSelection.name, () => {
  mockTenantStore();
  it("should display an input and respective title", () => {
    render(
      <ActivityTaskSelection
        activityTasks={dummyTasks}
        filteredTasks={[]}
        updateFilterHandler={mockUpdateFilterHandler}
      />
    );

    screen.getByText(/search and select a task from the list below/i);
    screen.getByPlaceholderText(/search by task or activity group/i);
  });

  it("should display an Empty State message when there are no tasks available", () => {
    render(
      <ActivityTaskSelection
        activityTasks={[]}
        filteredTasks={[]}
        updateFilterHandler={mockUpdateFilterHandler}
      />
    );
    screen.getByText(/no results found/i);
  });

  it("should display a list of accordions, matching the amount of grouped categories", () => {
    render(
      <ActivityTaskSelection
        activityTasks={dummyTasks}
        filteredTasks={[]}
        updateFilterHandler={mockUpdateFilterHandler}
      />
    );

    const groupedCategories = groupBy<LibraryTask>(dummyTasks, "category");
    const accordionsCount = screen.getAllByRole("button").length;
    expect(accordionsCount).toEqual(Object.keys(groupedCategories).length);
  });

  it("should call the updateFilterHandler function when a task is selected", () => {
    render(
      <ActivityTaskSelection
        activityTasks={dummyTasks}
        filteredTasks={[]}
        updateFilterHandler={mockUpdateFilterHandler}
      />
    );
    const category = screen.getByRole("button", {
      name: new RegExp(dummyTasks[0].category, "i"),
    });
    fireEvent.click(category);
    fireEvent.click(
      screen.getByRole("checkbox", {
        name: new RegExp(dummyTasks[0].name, "i"),
      })
    );
    expect(mockUpdateFilterHandler).toHaveBeenCalled();
  });

  describe("when performing a search and getting a match by category", () => {
    it("should display the category and at least one checkbox, as the category will be expanded", async () => {
      render(
        <ActivityTaskSelection
          activityTasks={dummyTasks}
          filteredTasks={[]}
          updateFilterHandler={mockUpdateFilterHandler}
        />
      );

      const inputText = dummyTasks[0].category;
      const element = screen.getByPlaceholderText(
        /search by task or activity group/i
      );
      fireEvent.change(element, {
        target: { value: inputText },
      });

      const tasksFound = await screen.findAllByRole("checkbox");
      const categoryFound = await screen.findByRole("button", {
        name: new RegExp(inputText, "i"),
      });

      expect(tasksFound.length).toBeGreaterThan(0);
      expect(categoryFound).toBeInTheDocument();
    });
  });

  describe("when performing a search and getting a match by task", () => {
    it("should display the matching task(s) and the corresponding category", async () => {
      render(
        <ActivityTaskSelection
          activityTasks={dummyTasks}
          filteredTasks={[]}
          updateFilterHandler={mockUpdateFilterHandler}
        />
      );

      const inputText = dummyTasks[0].name;
      const correspondingCategory = dummyTasks[0].category;
      const element = screen.getByPlaceholderText(
        /search by task or activity group/i
      );
      fireEvent.change(element, {
        target: { value: inputText },
      });

      await screen.findByRole("checkbox", {
        name: new RegExp(inputText, "i"),
      });
      await screen.findByRole("button", {
        name: new RegExp(correspondingCategory, "i"),
      });
    });
  });
});
