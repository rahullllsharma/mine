import { useTenantStore } from "@/store/tenant/useTenantStore.store";

enum ProjectStatus {
  PENDING = "PENDING",
  ACTIVE = "ACTIVE",
  COMPLETED = "COMPLETED",
}

type ProjectStatusOption = Readonly<{ id: ProjectStatus; name: string }[]>;

const projectStatusOptions = () =>
  Object.freeze(
    Object.values(ProjectStatus).map(state => ({
      id: state,
      name: useTenantStore
        .getState()
        .getMappingValue("status", state.toLowerCase()),
    }))
  );

export type { ProjectStatusOption };
export { ProjectStatus, projectStatusOptions };
