import type { ActivityFilter } from "@/container/activity/addActivityModal/AddActivityModal";
import type { LibraryTask } from "@/types/task/LibraryTask";
import {
  buildActivityName,
  getTaskListWithDuplicates,
  removeDuplicatedTaskIds,
} from "./activity.utils";

const taskWithMultipleActivGroups: LibraryTask[] = [
  {
    id: "task 1",
    name: "Rebar Install",
    category: "Civil Work",
    hazards: [],
    activitiesGroups: [
      {
        id: "1111",
        name: "Civil Work group",
      },
      {
        id: "2222",
        name: "Another group",
      },
    ],
  },
];

const filterListWithDuplicatedTasks: ActivityFilter[] = [
  {
    groupName: "Activity Group AA",
    values: [{ id: "aaaaa__11", name: "Task 1" }],
  },
  {
    groupName: "Activity Group BB",
    values: [{ id: "aaaaa__22", name: "Task 1" }],
  },
];

const shortFilterList: ActivityFilter[] = [
  { groupName: "Category A", values: [{ id: "1", name: "Task 1" }] },
  { groupName: "Category B", values: [{ id: "2", name: "Task 2" }] },
];

const longFilterList: ActivityFilter[] = [
  { groupName: "Category A", values: [{ id: "1", name: "Task 1" }] },
  { groupName: "Category B", values: [{ id: "2", name: "Task 2" }] },
  { groupName: "Category C", values: [{ id: "3", name: "Task 3" }] },
  { groupName: "Category D", values: [{ id: "4", name: "Task 4" }] },
];

describe("Activity helper", () => {
  describe("when there is a list with 3 or less results", () => {
    const expectedOutput = `${shortFilterList[0].groupName} + ${shortFilterList[1].groupName}`;

    it('should return all the categories, separated by " + "', () => {
      const result = buildActivityName(shortFilterList);
      expect(result).toEqual(expectedOutput);
    });
  });

  describe("when there is a list with more than 3 results", () => {
    const expectedOutput = `${longFilterList[0].groupName} + ${longFilterList[1].groupName} + (multiple)`;

    it('should return the first two categories, separated by " + " and the word "(multiple)" at the end', () => {
      const result = buildActivityName(longFilterList);
      expect(result).toEqual(expectedOutput);
    });
  });

  // Temporary tests to address task duplication and deduplication functions (WSAPP-972)
  describe("when there are Tasks with more than activityGroup", () => {
    it("the function getTaskListWithDuplicates() should return duplicated tasks, with different ids, and with only one ActivityGroup item", () => {
      expect(getTaskListWithDuplicates(taskWithMultipleActivGroups))
        .toMatchInlineSnapshot(`
        Array [
          Object {
            "activitiesGroups": Array [
              Object {
                "aliases": undefined,
                "id": "1111",
                "name": "Civil Work group",
              },
            ],
            "category": "Civil Work",
            "hazards": Array [],
            "id": "task 1__1111",
            "name": "Rebar Install",
          },
          Object {
            "activitiesGroups": Array [
              Object {
                "aliases": undefined,
                "id": "2222",
                "name": "Another group",
              },
            ],
            "category": "Civil Work",
            "hazards": Array [],
            "id": "task 1__2222",
            "name": "Rebar Install",
          },
        ]
      `);
    });

    it("the function removeDuplicatedTaskIds() should remove the duplicated tasks, and revert the id to its original state", () => {
      expect(removeDuplicatedTaskIds(filterListWithDuplicatedTasks))
        .toMatchInlineSnapshot(`
        Array [
          Object {
            "groupName": "Activity Group AA",
            "values": Array [
              Object {
                "id": "aaaaa",
                "name": "Task 1",
              },
            ],
          },
          Object {
            "groupName": "Activity Group BB",
            "values": Array [],
          },
        ]
      `);
    });
  });
});
