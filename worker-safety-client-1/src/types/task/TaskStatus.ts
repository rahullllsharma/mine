export enum TaskStatus {
  NOT_STARTED = "NOT_STARTED",
  IN_PROGRESS = "IN_PROGRESS",
  COMPLETE = "COMPLETE",
  NOT_COMPLETED = "NOT_COMPLETED",
}

// TODO: Should be through i18n
const taskStatusLabel = {
  [TaskStatus.NOT_STARTED]: "Not started",
  [TaskStatus.IN_PROGRESS]: "In-progress",
  [TaskStatus.COMPLETE]: "Complete",
  [TaskStatus.NOT_COMPLETED]: "Not completed",
};

export const taskStatusOptions = Object.freeze(
  Object.values(TaskStatus).map(state => ({
    id: state,
    name: taskStatusLabel[state],
  }))
);
