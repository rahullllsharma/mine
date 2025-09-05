import type { GetServerSideProps } from "next";
import MapView from "@/container/mapView/MapView";
import MapProvider from "@/container/mapView/context/MapProvider";
import TenantName from "@/graphql/queries/tenantName.gql";
import {
  authenticatedQuery,
  authGetServerSidePropsProxy,
} from "@/graphql/client";
import { useTenantFeatures } from "@/hooks/useTenantFeatures";
import { useAuthStore } from "@/store/auth/useAuthStore.store";

let flag = true;
const MapPage = () => {
  const { getLocationMapFilters } = useAuthStore();
  const storedFilters = getLocationMapFilters();

  let filters;

  if (storedFilters && storedFilters.length > 1) {
    filters = storedFilters;
  }

  if (flag) {
    flag = false;
    sessionStorage.clear();
  }
  return (
    <MapProvider defaultFilters={filters}>
      <MapView />
    </MapProvider>
  );
};

export default MapPage;

export const getServerSideProps: GetServerSideProps = async context =>
  authGetServerSidePropsProxy(context, async () => {
    const {
      data: { me },
    } = await authenticatedQuery(
      {
        query: TenantName,
      },
      context
    );
    const { displayMap } = useTenantFeatures(me.tenant.name);
    if (!displayMap) {
      return {
        redirect: {
          permanent: false,
          destination: "/404",
        },
      };
    }
    return { props: {} };
  });
