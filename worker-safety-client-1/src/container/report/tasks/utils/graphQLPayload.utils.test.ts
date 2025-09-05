import type { Location } from "@/types/project/Location";

import { tasks } from "@/graphql/mocks/tasks";
import { transformGraphQLPayload as graphQLPayload } from "./graphQLPayload.utils";

const location = {
  tasks,
} as Location;

describe(graphQLPayload.name, () => {
  it("should return an empty array when does not have tasks selected", () => {
    const {
      taskSelection: { selectedTasks },
    } = graphQLPayload({}, { location });
    expect(selectedTasks).toEqual([]);
  });

  it("should return an empty array when the selected tasks do not match the current tasks", () => {
    const {
      taskSelection: { selectedTasks },
    } = graphQLPayload({ taskSelection: { notFound: true } }, { location });
    expect(selectedTasks).toEqual([]);
  });

  it("should return array with the selected tasks with only some properties", () => {
    const {
      taskSelection: { selectedTasks },
    } = graphQLPayload(
      { taskSelection: { [tasks[0].id]: true, [tasks[1].id]: true } },
      { location }
    );

    expect(selectedTasks).toHaveLength(2);
    expect(selectedTasks[0]).toEqual({
      id: tasks[0].id,
      name: tasks[0].name,
      riskLevel: tasks[0].riskLevel,
    });
    expect(selectedTasks[1]).toEqual({
      id: tasks[1].id,
      name: tasks[1].name,
      riskLevel: tasks[1].riskLevel,
    });
  });
});
