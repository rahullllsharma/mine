import type { Project } from "@/types/project/Project";
import type { GetServerSideProps } from "next";
import { gql, useQuery } from "@apollo/client";
import ProjectSummaryView from "@/container/projectSummaryView/ProjectSummaryView";
import {
  authenticatedQuery,
  authGetServerSidePropsProxy,
} from "@/graphql/client";
import projectById from "@/graphql/queries/getProjectById.gql";
import { orderById, orderByName } from "@/graphql/utils";
import { convertDateToString, getDefaultDate } from "@/utils/date/helper";
import Loader from "@/components/shared/loader/Loader";

const projectDatesQuery = gql`
  query Project($projectId: UUID!) {
    project(projectId: $projectId) {
      id
      startDate
      endDate
    }
  }
`;

type ProjectSummaryViewPageProps = {
  project: Project;
};

export default function ProjectSummaryViewPage({
  project,
}: ProjectSummaryViewPageProps): JSX.Element {
  const today = convertDateToString();
  const date = getDefaultDate(project.startDate, project.endDate, today);

  const { data, loading } = useQuery(projectById, {
    variables: {
      projectId: project.id,
      date,
      isApplicable: true,
      controlsIsApplicable: true,
      orderBy: [orderByName],
      activitiesOrderBy: [orderByName, orderById],
      tasksOrderBy: [orderByName, orderById],
      hazardsOrderBy: [orderByName],
      controlsOrderBy: [orderByName],
      siteConditionsOrderBy: [orderByName, orderById],
      filterTenantSettings: true,
    },
    fetchPolicy: "cache-and-network",
  });

  if (loading) return <Loader />;

  return <ProjectSummaryView project={data.project} />;
}

export const getServerSideProps: GetServerSideProps = async context =>
  authGetServerSidePropsProxy(context, async () => {
    const { id } = context.query;

    const {
      data: { project },
    } = await authenticatedQuery(
      {
        query: projectDatesQuery,
        variables: {
          projectId: id,
        },
      },
      context
    );

    return {
      props: {
        project,
      },
    };
  });
