import type { ProjectStatus } from "@/types/project/ProjectStatus";
import { projectStatusOptions } from "@/types/project/ProjectStatus";

export const getProjectStatusById = (id: ProjectStatus) =>
  projectStatusOptions().find(option => option.id === id) as {
    id: ProjectStatus;
    name: string;
  };

export const getProjectStatusLabel = (status: ProjectStatus) =>
  getProjectStatusById(status).name as string;
