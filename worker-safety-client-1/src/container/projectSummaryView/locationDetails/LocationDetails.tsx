import type { Activity } from "@/types/activity/Activity";
import type {
  HazardAggregator,
  TaskHazardAggregator,
} from "@/types/project/HazardAggregator";
import type { Location } from "@/types/project/Location";
import type { DailyReport } from "@/types/report/DailyReport";
import type {
  TemplatesForm,
  TemplatesFormsList,
} from "@/types/Templates/TemplateLists";
import type { ActivitiesProps } from "./activities/Activities";
import type { SiteConditionsProps } from "./siteConditions/SiteConditions";
import router from "next/router";
import * as O from "fp-ts/lib/Option";
import { pipe } from "fp-ts/lib/function";
import { useContext, useEffect, useMemo, useState } from "react";
import { useCardStateManagement } from "@/hooks/useCardStateManagement";
import { useTenantFeatures } from "@/hooks/useTenantFeatures";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { jsbInfoCodec } from "@/types/project/JsbInfo";
import { config } from "@/config";
import useRestMutation from "@/hooks/useRestMutation";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import { messages } from "@/locales/messages";
import axiosRest from "@/api/restApi";
import LocationDetailsSection from "./LocationDetailsSection";
import { Activities } from "./activities/Activities";
import { ActivitiesEmpty } from "./activities/ActivitiesEmpty";
import SiteConditions from "./siteConditions/SiteConditions";
import TemplateForms from "./templateForms/TemplateForms";
import SiteConditionsEmpty from "./siteConditions/SiteConditionsEmpty";
import { withEmptyState } from "./withEmptyState";
import JsbSummary from "./jsb/JsbSummary";

type LocationDetailsProp = {
  location: Location;
  onTaskClick: (task: TaskHazardAggregator) => void;
  onAddTask: () => void;
  onSiteConditionClick: (siteCondition: HazardAggregator) => void;
  onAddSiteCondition: () => void;
  onDailyReportClick: (dailyReport: DailyReport) => void;
  onAddDailyReport: () => void;
  onAddActivity: () => void;
  projectStartDate: string;
  projectEndDate: string;
  projectId: string;
  startDate: string;
};

const getAggregatorKey = (aggregator: TaskHazardAggregator) =>
  `${aggregator.name}_${aggregator.id}`;

function LocationDetails({
  projectStartDate,
  projectEndDate,
  location,
  onTaskClick,
  onSiteConditionClick,
  onAddSiteCondition,
  onAddActivity,
  projectId,
  startDate,
}: LocationDetailsProp): JSX.Element {
  const { tenant, getAllEntities } = useTenantStore();
  const { siteCondition, activity } = getAllEntities();
  const { displayJSB } = useTenantFeatures(tenant.name);
  const toastCtx = useContext(ToastContext);

  const [isCardExpanded, setIsCardExpanded] = useCardStateManagement();
  const [cwfData, setCwfData] = useState([]);

  const isCardOpen = (aggregator: TaskHazardAggregator) =>
    isCardExpanded[getAggregatorKey(aggregator)] ?? false;

  const onToggleHandler = (aggregator: TaskHazardAggregator) =>
    setIsCardExpanded(getAggregatorKey(aggregator), !isCardOpen(aggregator));

  const handleOnSuccess = (response: any) => {
    const sortedTemplatesFormsData = response.data.data.sort(
      (a: TemplatesFormsList, b: TemplatesFormsList) =>
        a.group_by_key.localeCompare(b.group_by_key)
    );
    setCwfData(sortedTemplatesFormsData);
  };

  const handleOnError = () => {
    toastCtx?.pushToast("error", messages.SomethingWentWrong);
  };

  const { mutate: fetchTemplateReports } = useRestMutation<any>({
    endpoint: `${config.workerSafetyCustomWorkFlowUrlRest}/forms/list/`,
    method: "post",
    axiosInstance: axiosRest,
    dtoFn: data => data,
    mutationOptions: {
      onSuccess: (response: any) => {
        handleOnSuccess(response);
      },
      onError: () => {
        handleOnError();
      },
    },
  });

  const createRequestData = (locationId: string) => {
    return {
      work_package_id: [projectId],
      location_id: [locationId],
      group_by: "title",
      is_group_by_used: true,
      report_start_date: `${startDate}T00:00:00`,
      skip: 0,
      limit: 50,
      order_by: {
        field: "updated_at",
        desc: true,
      },
    };
  };

  useEffect(() => {
    const requestData = createRequestData(location.id);
    fetchTemplateReports(requestData);
  }, [projectId, startDate, location.id]);

  const ActivitiesListSection = withEmptyState<
    Activity,
    ActivitiesProps,
    TaskHazardAggregator
  >(Activities, {
    Empty: () => ActivitiesEmpty(onAddActivity),
    Container: function Container({ children }) {
      return (
        <LocationDetailsSection
          title={`${activity.labelPlural} (${location.activities.length})`}
        >
          {children}
        </LocationDetailsSection>
      );
    },
  });

  const SiteConditionsListSection = withEmptyState<
    HazardAggregator,
    SiteConditionsProps
  >(SiteConditions, {
    Empty: () => SiteConditionsEmpty(onAddSiteCondition),
    Container: function Container({ children }) {
      return (
        <LocationDetailsSection
          title={`${siteCondition.labelPlural} (${location.siteConditions.length})`}
        >
          {children}
        </LocationDetailsSection>
      );
    },
  });

  const gpsCoords = useMemo(
    () =>
      pipe(
        O.Do,
        O.bind("latitude", () => O.fromNullable(location.latitude)),
        O.bind("longitude", () => O.fromNullable(location.longitude))
      ),
    [location.latitude, location.longitude]
  );

  const viewReportFn = (formId: string) => {
    router.replace(
      `/template-forms/view?project=${projectId}&location=${location.id}&formId=${formId}&startDate=${startDate}`
    );
  };

  return (
    <div>
      {cwfData.length >= 0 &&
        cwfData.map((formGroup: TemplatesFormsList, formGroupIndex: number) => {
          return (
            <LocationDetailsSection
              key={formGroup.group_by_key}
              title={`${formGroup.group_by_key} (${formGroup?.forms?.length})`}
              isAccordionOpen={formGroupIndex === 0 ? true : false}
            >
              {formGroup &&
                formGroup.forms.map((form: TemplatesForm) => (
                  <TemplateForms
                    key={form.id}
                    element={form}
                    viewReportFn={() => viewReportFn(form.id)}
                    location={location}
                  />
                ))}
            </LocationDetailsSection>
          );
        })}
      {displayJSB &&
        location.jobSafetyBriefings &&
        location.jobSafetyBriefings.length > 0 && (
          <LocationDetailsSection
            title={`Forms (${location.jobSafetyBriefings.length})`}
          >
            {location.jobSafetyBriefings.map(jsb => {
              return (
                <JsbSummary
                  key={jsb.id}
                  jsbInfo={jsbInfoCodec.decode(jsb)}
                  gpsCoords={gpsCoords}
                  edit={() => {
                    router.push(
                      `/jsb?locationId=${location.id}&jsbId=${jsb.id}`
                    );
                  }}
                  location={location.id}
                />
              );
            })}
          </LocationDetailsSection>
        )}

      <div className="grid gap-6 grid-cols-1 col-span-2 xl:grid-cols-auto-fit-list-card mt-6 xl:mt-4">
        <SiteConditionsListSection
          elements={location.siteConditions}
          onElementClick={onSiteConditionClick}
          isCardOpen={isCardOpen}
          onCardToggle={onToggleHandler}
        />

        <ActivitiesListSection
          projectStartDate={projectStartDate}
          projectEndDate={projectEndDate}
          elements={location.activities}
          onElementClick={onTaskClick}
          isCardOpen={isCardOpen}
          onCardToggle={onToggleHandler}
        />
      </div>
    </div>
  );
}

export type { LocationDetailsProp };
export { LocationDetails };
