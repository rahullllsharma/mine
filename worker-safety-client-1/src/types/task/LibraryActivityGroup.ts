import type { LibraryTask } from "./LibraryTask";

type LibraryActivityGroup = {
  id: string;
  name: string;
  aliases?: string[];
  tasks?: LibraryTask[];
};

export type { LibraryActivityGroup };
