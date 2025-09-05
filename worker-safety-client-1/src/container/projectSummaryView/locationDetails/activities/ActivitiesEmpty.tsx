import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import EmptySection from "../EmptySection";

function ActivitiesEmpty(onAddActivity: () => void): JSX.Element {
  const { activity } = useTenantStore(state => state.getAllEntities());
  const { hasPermission } = useAuthStore();

  return (
    <EmptySection
      text={`There are no ${activity.labelPlural.toLowerCase()} scheduled for today`}
      buttonLabel={`Add an ${activity.label.toLowerCase()}`}
      onClick={hasPermission("ADD_ACTIVITIES") ? onAddActivity : undefined}
    />
  );
}

export { ActivitiesEmpty };
