import { useTenantStore } from "@/store/tenant/useTenantStore.store";

const getActivityTaskName = () => {
  const { activity, task } = useTenantStore.getState().getAllEntities();
  return `${activity.label} ${task.labelPlural}`;
};

export { getActivityTaskName };
