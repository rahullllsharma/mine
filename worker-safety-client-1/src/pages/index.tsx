import type { GetServerSideProps } from "next";
import {
  authenticatedQuery,
  authGetServerSidePropsProxy,
} from "@/graphql/client";
import Permissions from "@/graphql/queries/permissions.gql";
import { useTenantFeatures } from "@/hooks/useTenantFeatures";

function LandingPage(): JSX.Element {
  return <></>;
}

const getHomePagePath = (
  tenantFeatures: ReturnType<typeof useTenantFeatures>
): string => {
  const homePagePathMap = {
    map: "/map",
    projects: "/projects",
    forms: "/forms",
    templateForms: "/template-forms",
  };
  const {
    displayProjectsAsLandingPage,
    displayFormsAsLandingPage,
    displayTemplateFormsAsLandingPage,
  } = tenantFeatures;
  if (displayProjectsAsLandingPage) {
    return homePagePathMap.projects;
  } else if (displayFormsAsLandingPage) {
    return homePagePathMap.forms;
  } else if (displayTemplateFormsAsLandingPage) {
    return homePagePathMap.templateForms;
  }

  // Default home is /map
  return homePagePathMap.map;
};

export const getServerSideProps: GetServerSideProps = async context =>
  authGetServerSidePropsProxy(context, async () => {
    const {
      data: { me },
    } = await authenticatedQuery(
      {
        query: Permissions,
      },
      context
    );
    return {
      redirect: {
        destination: getHomePagePath(useTenantFeatures(me.tenant.name)),
        permanent: false,
      },
    };
  });

export default LandingPage;
