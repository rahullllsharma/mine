import type { Project } from "@/types/project/Project";

function filterByUserId(project: Project, userId = "") {
  const { manager, supervisor, additionalSupervisors } = project;
  return (
    manager?.id === userId ||
    supervisor?.id === userId ||
    additionalSupervisors?.some(({ id }) => id === userId)
  );
}

export { filterByUserId };
