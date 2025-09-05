import type { GetServerSideProps } from "next";
import type { DailyInspectionReport as DailyInspectionReportProps } from "@/container/report/dailyInspection/types";

import {
  authenticatedQuery,
  authGetServerSidePropsProxy,
} from "@/graphql/client";

import getProjectByIdEdit from "@/graphql/queries/getProjectByIdEdit.gql";
import getDailyReport from "@/graphql/queries/dailyReport/getDailyReport.gql";
import getProjectLocations from "@/graphql/queries/dailyReport/getProjectLocationsWithoutDailyReports.gql";
import TenantName from "@/graphql/queries/tenantName.gql";

import DailyInspection from "@/container/report/dailyInspection/DailyInspection";
import { stripTypename } from "@/utils/shared";
import { convertDateToString, getDefaultDate } from "@/utils/date/helper";
import { useTenantFeatures } from "@/hooks/useTenantFeatures";

export default function EditDailyReportPage(
  props: Omit<DailyInspectionReportProps, "dailyReport">
): JSX.Element {
  return <DailyInspection {...props} />;
}

export const getServerSideProps: GetServerSideProps = async context =>
  authGetServerSidePropsProxy(context, async () => {
    //TODO Needs to be revised when we switch to feature flags
    //https://urbint.atlassian.net/browse/WSAPP-1210
    const {
      data: { me },
    } = await authenticatedQuery(
      {
        query: TenantName,
      },
      context
    );

    const { displayInspections } = useTenantFeatures(me.tenant.name);

    if (!displayInspections) {
      return {
        redirect: {
          permanent: false,
          destination: "/404",
        },
      };
    }

    const {
      id: projectId,
      locationId,
      dailyReportId,
      startDate,
    } = context.query;

    try {
      const {
        data: { project },
        error,
      } = await authenticatedQuery(
        {
          query: getProjectByIdEdit,
          variables: { projectId },
        },
        context
      );

      if (error) {
        return {
          notFound: true,
        };
      }

      const [responseProjectLocation, responseDailyReport] = await Promise.all([
        // Fetch details about the location
        authenticatedQuery(
          {
            query: getProjectLocations,
            variables: {
              projectLocationsId: locationId,
              isApplicable: true,
              controlsIsApplicable: true,
              date: startDate,
            },
          },
          context
        ),
        // Fetch daily inspection report details
        authenticatedQuery(
          {
            query: getDailyReport,
            variables: {
              id: dailyReportId,
            },
          },
          context
        ),
      ]);

      const {
        data: { projectLocations: locations, recommendations },
        error: projectLocationsError,
      } = responseProjectLocation;

      const {
        data: { dailyReport },
        error: dailyReportError,
      } = responseDailyReport;

      // TODO: Enter the proper rules once we have more sections.
      // - User enters `report/`
      //   => 301 redirect to `project/{id}/location/{location}/report`
      // - User enters `report/gibberish`
      //   => 400 redirect to `project/{id}/`
      if (
        projectLocationsError ||
        dailyReportError ||
        !locations ||
        !dailyReport
      ) {
        return {
          notFound: true,
        };
      }

      // TODO: Do we need to handle TZ conversions?
      return {
        props: stripTypename({
          project,
          recommendations: recommendations?.dailyReport || null,
          location: locations[0],
          dailyReport,
          projectSummaryViewDate: getDefaultDate(
            project.startDate,
            project.endDate,
            (startDate as string) || convertDateToString()
          ),
        }),
      };
    } catch (e) {
      console.log(
        "Daily Inspection Report - edit page = ups, something failed completely: ",
        { e }
      );
      return {
        notFound: true,
      };
    }
  });
