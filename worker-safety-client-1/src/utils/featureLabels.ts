import { useTenantStore } from "@/store/tenant/useTenantStore.store";

const getFeatureLabels = () => {
  const { getAllEntities } = useTenantStore.getState();
  const { workPackage, location, activity } = getAllEntities();

  return {
    VALUES: {
      ACTIVITY: activity?.key,
      LOCATION: location?.key,
      WORK_PACKAGE: workPackage?.key,
    },
  };
};

export { getFeatureLabels };
