import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import EmptySection from "../EmptySection";

export default function SiteConditionsEmptySection(
  onAddSiteCondition: () => void
): JSX.Element {
  const { workPackage, siteCondition } = useTenantStore(state =>
    state.getAllEntities()
  );
  const { hasPermission } = useAuthStore();
  return (
    <EmptySection
      text={`There are no ${siteCondition.labelPlural.toLowerCase()} affecting your ${workPackage.label.toLowerCase()} today`}
      buttonLabel={`Add a ${siteCondition.label.toLowerCase()}`}
      onClick={
        hasPermission("ADD_SITE_CONDITIONS") ? onAddSiteCondition : undefined
      }
    />
  );
}
