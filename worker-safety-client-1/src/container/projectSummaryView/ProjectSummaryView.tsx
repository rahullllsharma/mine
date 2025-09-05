import type { PageHeaderAction } from "@/components/layout/pageHeader/components/headerActions/HeaderActions";
import type { RiskLevel } from "@/components/riskBadge/RiskLevel";
import type { SelectPrimaryOption } from "@/components/shared/select/selectPrimary/SelectPrimary";
import type { Location } from "@/types/project/Location";
import type { Project } from "@/types/project/Project";
import type { CriticalActivityType } from "../report/dailyInspection/types";
import { useLazyQuery } from "@apollo/client";
import cx from "classnames";
import { useRouter } from "next/router";
import { lazy, Suspense, useRef, useState } from "react";
import { isMobile, isMobileOnly, isTablet } from "react-device-detect";
import PageHeader from "@/components/layout/pageHeader/PageHeader";
import PageLayout from "@/components/layout/pageLayout/PageLayout";
import RiskBadge from "@/components/riskBadge/RiskBadge";
import Tooltip from "@/components/shared/tooltip/Tooltip";
import ProjectRiskByDate from "@/graphql/queries/getProjectRiskByDate.gql";
import ProjectLocations from "@/graphql/queries/projectLocations.gql";
import ProjectLocationsWithCritical from "@/graphql/queries/projectLocationsWithCritical.gql";
import { orderById, orderByName } from "@/graphql/utils";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { convertDateToString, getDefaultDate } from "@/utils/date/helper";
import {
  getUpdatedRouterQuery,
  pushHistoryStateQueryParam,
} from "@/utils/router";
import { ProjectSummaryViewProvider } from "./context/ProjectSummaryContext";
import ProjectDailyPlan from "./dailyPlan/ProjectDailyPlan";
import { ProjectSummaryViewHeader } from "./header/ProjectSummaryViewHeader";
import { ProjectDescriptionHeader } from "./PojectDescriptionHeader";
import { getBreadcrumbDetails, getLocationById } from "./utils";

const AddActivityModal = lazy(
  () => import("../activity/addActivityModal/AddActivityModal")
);
const AddSiteConditionModal = lazy(
  () => import("../siteCondition/addSiteConditionModal/AddSiteConditionModal")
);

//FIXME: Remove task from the list of options
export type SummaryViewContentType =
  | "task"
  | "siteCondition"
  | "report"
  | "activity";
type ProjectSummaryViewProps = {
  project: Project;
};

// Future fallback comment, incase this needs to be reverted
// A lot of this component was trimmed in:
// https://urbint.atlassian.net/browse/WSAPP-1227
export default function ProjectSummaryView({
  project,
}: ProjectSummaryViewProps): JSX.Element {
  const { workPackage, location: locationEntity } = useTenantStore(state =>
    state.getAllEntities()
  );

  const {
    id,
    name,
    description,
    locations,
    riskLevel: projectRiskLevel,
    startDate: projectStartDate,
    endDate: projectEndDate,
  } = project;
  const router = useRouter();
  const [selectedModalType, setSelectedModalType] =
    useState<SummaryViewContentType | null>();

  const [location, setLocation] = useState<Location>(
    getLocationById(locations, router.query.location as string)
  );
  const source = router.query.source as string;
  const breadcrumb = getBreadcrumbDetails(workPackage.labelPlural, source);

  const [riskLevel, setRiskLevel] = useState<RiskLevel>(projectRiskLevel);
  const [criticalActivityData, setCriticalActivityData] = useState<
    CriticalActivityType[]
  >([]);
  const [criticalActivityStartDate, setCriticalActivityStartDate] =
    useState<string>("");
  const [criticalActivityEndDate, setCriticalActivityEndDate] =
    useState<string>("");
  const taskSearchRef = useRef<HTMLInputElement>(null);

  const { hasPermission } = useAuthStore();
  const [getProjectLocation] = useLazyQuery(ProjectLocations, {
    fetchPolicy: "cache-and-network",
    onCompleted: ({ projectLocations }) => {
      const projectLocation = projectLocations[0];
      setLocation(projectLocation);
      pushHistoryStateQueryParam("location", projectLocation.id);
    },
  });
  const [getProjectRiskByDate] = useLazyQuery(ProjectRiskByDate, {
    fetchPolicy: "cache-and-network",
    onCompleted: data => {
      setRiskLevel(data.project.riskLevel);
    },
  });

  const today = router.query.startDate
    ? convertDateToString(String(router.query.startDate))
    : convertDateToString();
  const [currentDate, setCurrentDate] = useState(
    getDefaultDate(projectStartDate, projectEndDate, today)
  );

  const getProjectLocationHandler = ({
    projectLocationId = location.id,
    date = currentDate,
  }: {
    projectLocationId?: string;
    date?: string;
  } = {}) => {
    getProjectLocation({
      variables: {
        projectLocationId,
        date,
        isApplicable: true,
        controlsIsApplicable: true,
        activitiesOrderBy: [orderByName, orderById],
        tasksOrderBy: [orderByName, orderById],
        hazardsOrderBy: [orderByName],
        controlsOrderBy: [orderByName],
        siteConditionsOrderBy: [orderByName, orderById],
        filterTenantSettings: true,
      },
    });
    getProjectRiskByDate({ variables: { projectId: id, date } });
    getCriticalActivityForDates({
      projectLocationId: location.id,
      startDate: criticalActivityStartDate || currentDate,
      endDate: criticalActivityEndDate || currentDate,
    });
  };
  const [getProjectLocationWithCritical] = useLazyQuery(
    ProjectLocationsWithCritical,
    {
      fetchPolicy: "cache-and-network",
      onCompleted: ({ projectLocations }) => {
        const criticalActivityDataResponse =
          projectLocations[0]?.dailySnapshots;
        setCriticalActivityData(criticalActivityDataResponse);
      },
    }
  );
  const getCriticalActivityForDates = ({
    projectLocationId = location.id,
    startDate,
    endDate,
  }: {
    projectLocationId?: string;
    startDate?: string;
    endDate?: string;
  } = {}) => {
    getProjectLocationWithCritical({
      variables: {
        projectLocationId,
        dateRange: { startDate: startDate, endDate: endDate },
      },
    });
  };

  const locationSelectHandler = (option: SelectPrimaryOption) => {
    // TODO: can this if be removed?
    if (taskSearchRef.current) {
      taskSearchRef.current.value = "";
    }
    const projectLocationId = option.id as string;
    getProjectLocationHandler({
      projectLocationId,
    });
    getCriticalActivityForDates({
      projectLocationId: location.id,
      startDate: criticalActivityStartDate || currentDate,
      endDate: criticalActivityEndDate || currentDate,
    });
  };

  const actionClickHandler = () =>
    router.push({
      pathname: "/projects/[id]/settings",
      query: getUpdatedRouterQuery(
        { id },
        { key: "source", value: router.query.source }
      ),
    });
  const headerAction: PageHeaderAction | undefined = hasPermission(
    "VIEW_PROJECT"
  )
    ? {
        icon: "settings_filled",
        title: "settings",
        onClick: actionClickHandler,
      }
    : undefined;

  const addContentHandler = (type: SummaryViewContentType) => {
    if (type === "report") {
      const query = getUpdatedRouterQuery(
        {
          id,
          locationId: location.id,
          startDate: currentDate,
          pathOrigin: "workPackage",
        },
        { key: "source", value: router.query.source }
      );

      router.push({
        pathname: "/projects/[id]/locations/[locationId]/reports",
        query,
      });
    } else {
      setSelectedModalType(type);
    }
  };

  const closeModalHandler = () => {
    setSelectedModalType(null);
    getCriticalActivityForDates({
      projectLocationId: location.id,
      startDate: criticalActivityStartDate || currentDate,
      endDate: criticalActivityEndDate || currentDate,
    });
  };

  const isSiteConditionModalOpen = selectedModalType === "siteCondition";

  const isActivityModalOpen = selectedModalType === "activity";

  const addSiteConditionSuccessHandler = () =>
    getProjectLocationHandler({ projectLocationId: location.id });

  const dateSelectHandler = (date: string) => {
    setCurrentDate(date);
    getProjectLocationHandler({ date });
  };

  const dateRangeNavigator = (startDate: string, endDate: string) => {
    setCriticalActivityStartDate(startDate);
    setCriticalActivityEndDate(endDate);
    getCriticalActivityForDates({
      projectLocationId: location.id,
      startDate,
      endDate,
    });
  };

  const totalActivities = location.activities;
  const isCritical =
    totalActivities?.some(data => data?.isCritical === true) || false;

  return (
    <ProjectSummaryViewProvider
      refetchActivitiesBasedOnLocation={() => getProjectLocationHandler({})}
    >
      <PageLayout
        header={
          <>
            <PageHeader
              linkText={breadcrumb.title}
              linkRoute={breadcrumb.link}
              actions={headerAction}
              additionalInfo={
                description && (
                  <ProjectDescriptionHeader
                    maxCharacters={isMobileOnly ? 35 : 80}
                    description={description}
                  />
                )
              }
            >
              <div className="flex flex-col w-full">
                <div className="flex-row flex">
                  <h4 className="text-neutral-shade-100 mr-3">{name}</h4>
                  <Tooltip
                    title={`${
                      workPackage.label
                    } risk is based on risk across all ${workPackage.label.toLowerCase()} ${locationEntity.labelPlural.toLowerCase()}`}
                    className="max-w-[200px] md:max-w-full pl-10"
                  >
                    <RiskBadge
                      risk={riskLevel}
                      label={`${riskLevel}`}
                      isCritical={isCritical}
                    />
                  </Tooltip>
                </div>
              </div>
            </PageHeader>
          </>
        }
        className={cx("flex-1", { ["mb-12"]: isMobile || isTablet })}
      >
        <section className="responsive-padding-x">
          <div className="flex items-start md:items-center mb-6 justify-between">
            <ProjectSummaryViewHeader
              locations={locations}
              selectedLocation={location}
              projectContractorId={project.contractor?.id}
              projectRegionId={project.libraryRegion?.id}
              onLocationSelected={locationSelectHandler}
              onAddContent={addContentHandler}
              isCritical={isCritical}
              startDate={currentDate}
              projectWorkTypes={project.workTypes}
            />
          </div>
          <div className="mt-6">
            <div>
              <ProjectDailyPlan
                project={project}
                location={location}
                onDateSelect={dateSelectHandler}
                dateRangeNavigator={dateRangeNavigator} // function
                currentDate={currentDate}
                onAddTask={() => addContentHandler("task")}
                onAddSiteCondition={() => addContentHandler("siteCondition")}
                onAddDailyReport={() => addContentHandler("report")}
                onAddActivity={() => addContentHandler("activity")}
                isCritical={isCritical}
                criticalActivityData={criticalActivityData}
              />
            </div>
          </div>
        </section>

        <Suspense fallback={null}>
          {isSiteConditionModalOpen && (
            <AddSiteConditionModal
              isOpen={isSiteConditionModalOpen}
              closeModal={closeModalHandler}
              locationId={location.id}
              addSiteConditionSuccessHandler={addSiteConditionSuccessHandler}
              siteConditions={location.siteConditions}
              projectWorkTypes={project.workTypes}
            />
          )}

          {isActivityModalOpen && (
            <AddActivityModal
              isOpen={isActivityModalOpen}
              closeModal={closeModalHandler}
              projectStartDate={projectStartDate}
              projectEndDate={projectEndDate}
              startDate={currentDate}
              locationId={location.id}
              projectWorkTypes={project.workTypes}
            />
          )}
        </Suspense>
      </PageLayout>
    </ProjectSummaryViewProvider>
  );
}
