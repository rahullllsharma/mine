import type { FormFilter } from "@/container/insights/filters/formFilters/FormFilters";
import type { Form } from "@/types/formsList/formsList";
import type { ChangeEvent } from "react";
import type { GetServerSideProps } from "next";
import { useLazyQuery } from "@apollo/client";
import { debounce } from "lodash-es";
import { useContext, useEffect, useMemo, useState } from "react";
import router from "next/router";
import { isMobile } from "react-device-detect";
import TenantName from "@/graphql/queries/tenantName.gql";
import EmptyContent from "@/components/emptyContent/EmptyContent";
import PageLayout from "@/components/layout/pageLayout/PageLayout";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import Input from "@/components/shared/input/Input";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import { List as FormsList } from "@/container/formsList/list/List";
import FormFilters from "@/container/insights/filters/formFilters/FormFilters";
import GetFormsList from "@/graphql/queries/getFormsList.gql";
import GetFormsListCount from "@/graphql/queries/getFormsListCount.gql";
import { orderByUpdatedAt } from "@/graphql/utils";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { getFormattedDate } from "@/container/insights/utils";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import Dropdown from "@/components/shared/dropdown/Dropdown";
import { sessionExpiryHandlerForApolloClient } from "@/utils/auth";
import {
  authenticatedQuery,
  authGetServerSidePropsProxy,
} from "../../graphql/client";
import { useTenantFeatures } from "../../hooks/useTenantFeatures";

/** Only used for the initial request */
const GET_FORMS_LIST_OFFSET = 0;

/** Total projects per request */
const GET_FORMS_LIST_LIMIT = 50;

const getFormsListState = ({
  loading,
}: {
  current?: Form[];
  loading?: boolean;
}) => {
  if (loading) {
    return "loading";
  }

  return undefined;
};

type FormsPageProps = {
  displayAddEbo: boolean;
  displayAddJsb: boolean;
  displayAddForm: boolean;
};

const VARIABLES = {
  limit: GET_FORMS_LIST_LIMIT,
  offset: GET_FORMS_LIST_OFFSET,
  orderBy: [orderByUpdatedAt],
};

export default function FormsPage({
  displayAddEbo,
  displayAddJsb,
  displayAddForm,
}: FormsPageProps): JSX.Element {
  const { isViewer, getFormFilters } = useAuthStore();
  const { formList } = useTenantStore(state => state.getAllEntities());
  const [showFilters, setShowFilters] = useState<boolean>(false);
  const [totalFiltersSelected, setTotalFiltersSelected] = useState<number>();
  const toastCtx = useContext(ToastContext);
  const [search, setSearch] = useState("");
  const [disableFetchMore, setDisableFetchMore] = useState(false);
  const [createdByIds, setCreatedByIds] = useState<string[]>([]);
  const [updatedByIds, setUpdatedByIds] = useState<string[]>([]);
  const [formName, setFormName] = useState<string[]>([]);
  const [formId, setFormId] = useState<string[]>([]);
  const [locationIds, setLocationIds] = useState<string[]>([]);
  const [status, setStatus] = useState<string[]>([]);
  const [workPackage, setWorkPackage] = useState<string[]>([]);
  const [adHocForms, setAdHocForms] = useState<boolean>(false);
  const [createdOnStartDate, setCreatedOnStartDate] = useState<string>("");
  const [createdOnEndDate, setCreatedOnEndDate] = useState<string>("");
  const [updatedOnStartDate, setUpdatedOnStartTime] = useState<string>("");
  const [updatedOnEndDate, setUpdatedOnEndTime] = useState<string>("");
  const [completedOnStartDate, setCompletedOnStartDate] = useState<string>("");
  const [completedOnEndDate, setCompletedOnEndDate] = useState<string>("");
  const [reportDateStartDate, setReportDateStartDate] = useState<string>("");
  const [reportDateEndDate, setReportDateEndDate] = useState<string>("");
  const [managerIds, setManagerIds] = useState<string[]>([]);
  const [operatingRegionNames, setOperatingRegionNames] = useState<string[]>(
    []
  );

  const [getFormsListCount, { data: { formsListCount = null } = {} }] =
    useLazyQuery<{
      formsListCount: number;
    }>(GetFormsListCount, {
      fetchPolicy: "cache-and-network",
    });

  const [getFormsList, { loading, fetchMore, data: { formsList = [] } = {} }] =
    useLazyQuery<{ formsList: Form[] }>(GetFormsList, {
      fetchPolicy: "cache-and-network",
      onError: error => {
        toastCtx?.pushToast("error", "Error searching");
        sessionExpiryHandlerForApolloClient(error);
      },
    });

  useEffect(() => {
    const storedFilters: FormFilter[] = getFormFilters() ?? [];
    handleFilterUpdate(storedFilters);
  }, []);

  const addFormsClick = () => router.push("/ebo");

  const addJsbClick = () =>
    router.push({
      pathname: "/jsb",
      query: {
        pathOrigin: "forms",
      },
    });

  const menuItems = [];

  if (displayAddEbo && !isViewer()) {
    menuItems.push({
      label: "Energy Based Observation",
      onClick: addFormsClick,
    });
  }

  if (displayAddJsb && !isViewer()) {
    menuItems.push({ label: "Job Safety Briefing", onClick: addJsbClick });
  }

  const toggleFilters = () => setShowFilters(prevState => !prevState);

  const handleFilterUpdate = (filters: FormFilter[]) => {
    setShowFilters(false);
    const getValueById = (field: string) =>
      filters
        .find(data => data.field === field)
        ?.values.map(value => value.id) || [];

    const getValueByName = (field: string) =>
      filters
        .find(data => data.field === field)
        ?.values.map(value => value.name) || [];

    const getValues = (field: string) =>
      filters.find(data => data.field === field)?.values || [];

    const createdById = getValueById("CREATEDBY");
    setCreatedByIds(createdById);
    const updatedById = getValueById("UPDATEDBY");
    setUpdatedByIds(updatedById);
    const formsName = getValueById("FORM").map(id => id);
    setFormName(formsName);

    const searchFormId = getValueById("FORMID");
    setFormId(searchFormId);

    const locationId = getValueById("LOCATIONS");
    setLocationIds(locationId);
    const statuses = getValueByName("STATUS").map(name =>
      name.toUpperCase().replace(/-/g, "_")
    );

    for (let i = 0; i < statuses.length; i++) {
      if (statuses[i] === "PENDING POST JOB BRIEF")
        statuses[i] = "PENDING_POST_JOB_BRIEF";
      if (statuses[i] === "PENDING SIGN OFF") statuses[i] = "PENDING_SIGN_OFF";
    }
    setStatus(statuses);

    const localOperatingRegionNames = getValueByName("OPERATINGHQ");
    setOperatingRegionNames(localOperatingRegionNames);

    const workPackageIds = getValueById("WORKPACKAGE").filter(id => id !== "");
    const workpackageNames = getValueByName("WORKPACKAGE");
    const adhocWorkpackage = !!workpackageNames.find(wp => wp === "AD_HOC");
    if (adhocWorkpackage) {
      setAdHocForms(true);
      setWorkPackage([]);
    } else {
      setAdHocForms(false);
      setWorkPackage(workPackageIds);
    }

    const localManagerIds = getValueById("SUPERVISOR").filter(id => id !== "");
    setManagerIds(localManagerIds);

    const createdOnTimeRange = getValues("CREATEDON");
    setCreatedOnStartDate(createdOnTimeRange[0]?.name);
    setCreatedOnEndDate(createdOnTimeRange[1]?.name);
    const updatedOnTimeRange = getValues("UPDATEDON");
    setUpdatedOnStartTime(updatedOnTimeRange[0]?.name);
    setUpdatedOnEndTime(updatedOnTimeRange[1]?.name);
    const completedOnTimeRange = getValues("COMPLETEDON");
    setCompletedOnStartDate(completedOnTimeRange[0]?.name);
    setCompletedOnEndDate(completedOnTimeRange[1]?.name);
    const reportDateTimeRange = getValues("REPORTDATE");
    setReportDateStartDate(reportDateTimeRange[0]?.name);
    setReportDateEndDate(reportDateTimeRange[1]?.name);
    setDisableFetchMore(false);

    const commonVariables = {
      search: search || null,
      adHoc: adhocWorkpackage,
      createdByIds: createdById.length > 0 ? createdById : null,
      formName: formsName.length > 0 ? formsName : null,
      formId: searchFormId.length > 0 ? searchFormId : null,
      locationIds: locationId.length > 0 ? locationId : null,
      formStatus: statuses.length > 0 ? statuses : null,
      projectIds: workPackageIds.length > 0 ? workPackageIds : null,
      startCreatedAt: createdOnTimeRange[0]
        ? getFormattedDate(new Date(createdOnTimeRange[0].name), {
            format: "yyyy-MM-dd",
          })
        : null,
      endCreatedAt: createdOnTimeRange[1]
        ? getFormattedDate(new Date(createdOnTimeRange[1].name), {
            format: "yyyy-MM-dd",
          })
        : null,
      updatedByIds: updatedById.length > 0 ? updatedById : null,
      startUpdatedAt: updatedOnTimeRange[0]
        ? getFormattedDate(new Date(updatedOnTimeRange[0].name), {
            format: "yyyy-MM-dd",
          })
        : null,
      endUpdatedAt: updatedOnTimeRange[1]
        ? getFormattedDate(new Date(updatedOnTimeRange[1].name), {
            format: "yyyy-MM-dd",
          })
        : null,
      startCompletedAt: completedOnTimeRange[0]
        ? getFormattedDate(new Date(completedOnTimeRange[0].name), {
            format: "yyyy-MM-dd",
          })
        : null,
      endCompletedAt: completedOnTimeRange[1]
        ? getFormattedDate(new Date(completedOnTimeRange[1].name), {
            format: "yyyy-MM-dd",
          })
        : null,
      startReportDate: reportDateTimeRange[0]
        ? getFormattedDate(new Date(reportDateTimeRange[0].name), {
            format: "yyyy-MM-dd",
          })
        : null,
      endReportDate: reportDateTimeRange[1]
        ? getFormattedDate(new Date(reportDateTimeRange[1].name), {
            format: "yyyy-MM-dd",
          })
        : null,
      operatingRegionNames: localOperatingRegionNames.length
        ? localOperatingRegionNames
        : null,
      managerIds: localManagerIds.length ? localManagerIds : null,
    };

    getFormsListCount({ variables: commonVariables });

    getFormsList({
      variables: {
        ...VARIABLES,
        ...commonVariables,
      },
    });
    const totalFilterSelected = filters.reduce(
      (acc, filter) => acc + filter.values.length,
      0
    );
    setTotalFiltersSelected(
      createdOnTimeRange[1] ? totalFilterSelected - 1 : totalFilterSelected
    );
    setTotalFiltersSelected(
      updatedOnTimeRange[1] ? totalFilterSelected - 1 : totalFilterSelected
    );
  };

  const onChange = debounce((text: ChangeEvent<HTMLInputElement>) => {
    const searchTerm = text.target.value;

    setSearch(searchTerm);

    const commonVariables = {
      adHoc: adHocForms,
      search: searchTerm || null,
      createdByIds: createdByIds.length > 0 ? createdByIds : null,
      formName: formName.length > 0 ? formName : null,
      formId: formId.length > 0 ? formId : null,
      locationIds: locationIds.length > 0 ? locationIds : null,
      formStatus: status.length > 0 ? status : null,
      projectIds: workPackage.length > 0 ? workPackage : null,
      startCreatedAt: createdOnStartDate
        ? getFormattedDate(new Date(createdOnStartDate), {
            format: "yyyy-MM-dd",
          })
        : null,
      endCreatedAt: createdOnEndDate
        ? getFormattedDate(new Date(createdOnEndDate), {
            format: "yyyy-MM-dd",
          })
        : null,
      updatedByIds: updatedByIds.length > 0 ? updatedByIds : null,
      startUpdatedAt: updatedOnStartDate
        ? getFormattedDate(new Date(updatedOnStartDate), {
            format: "yyyy-MM-dd",
          })
        : null,
      endUpdatedAt: updatedOnEndDate
        ? getFormattedDate(new Date(updatedOnEndDate), {
            format: "yyyy-MM-dd",
          })
        : null,
      startCompletedAt: completedOnStartDate
        ? getFormattedDate(new Date(completedOnStartDate), {
            format: "yyyy-MM-dd",
          })
        : null,
      endCompletedAt: completedOnEndDate
        ? getFormattedDate(new Date(completedOnEndDate), {
            format: "yyyy-MM-dd",
          })
        : null,
      startReportDate: reportDateStartDate
        ? getFormattedDate(new Date(reportDateStartDate), {
            format: "yyyy-MM-dd",
          })
        : null,
      endReportDate: reportDateEndDate
        ? getFormattedDate(new Date(reportDateEndDate), {
            format: "yyyy-MM-dd",
          })
        : null,
      operatingRegionNames: operatingRegionNames.length
        ? operatingRegionNames
        : null,
      managerIds: managerIds.length ? managerIds : null,
    };

    setDisableFetchMore(false);

    getFormsListCount({ variables: commonVariables });

    getFormsList({
      variables: {
        ...VARIABLES,
        ...commonVariables,
        offset: 0,
      },
    });
  }, 200);

  const onLoadMoreFormsList = () => {
    const commonVariables = {
      adHoc: adHocForms,
      search: search || null,
      createdByIds: createdByIds.length > 0 ? createdByIds : null,
      formName: formName.length > 0 ? formName : null,
      formId: formId.length > 0 ? formId : null,
      locationIds: locationIds.length > 0 ? locationIds : null,
      formStatus: status.length > 0 ? status : null,
      projectIds: workPackage.length > 0 ? workPackage : null,
      startCreatedAt: createdOnStartDate
        ? getFormattedDate(new Date(createdOnStartDate), {
            format: "yyyy-MM-dd",
          })
        : null,
      endCreatedAt: createdOnEndDate
        ? getFormattedDate(new Date(createdOnEndDate), {
            format: "yyyy-MM-dd",
          })
        : null,
      updatedByIds: updatedByIds.length > 0 ? updatedByIds : null,
      startUpdatedAt: updatedOnStartDate
        ? getFormattedDate(new Date(updatedOnStartDate), {
            format: "yyyy-MM-dd",
          })
        : null,
      endUpdatedAt: updatedOnEndDate
        ? getFormattedDate(new Date(updatedOnEndDate), {
            format: "yyyy-MM-dd",
          })
        : null,
      startCompletedAt: completedOnStartDate
        ? getFormattedDate(new Date(completedOnStartDate), {
            format: "yyyy-MM-dd",
          })
        : null,
      endCompletedAt: completedOnEndDate
        ? getFormattedDate(new Date(completedOnEndDate), {
            format: "yyyy-MM-dd",
          })
        : null,
      startReportDate: reportDateStartDate
        ? getFormattedDate(new Date(reportDateStartDate), {
            format: "yyyy-MM-dd",
          })
        : null,
      endReportDate: reportDateEndDate
        ? getFormattedDate(new Date(reportDateEndDate), {
            format: "yyyy-MM-dd",
          })
        : null,
      operatingRegionNames: operatingRegionNames.length
        ? operatingRegionNames
        : null,
      managerIds: managerIds.length ? managerIds : null,
    };

    if (disableFetchMore) return;

    fetchMore &&
      fetchMore({
        variables: {
          ...VARIABLES,
          ...commonVariables,
          offset: formsList.length,
        },
        updateQuery: (prev, { fetchMoreResult }) => {
          if (!fetchMoreResult) return prev;
          if (fetchMoreResult.formsList.length === 0) setDisableFetchMore(true);
          return Object.assign({}, prev, {
            formsList: [...prev.formsList, ...fetchMoreResult.formsList],
          });
        },
      });
  };

  const uiState = useMemo(
    () =>
      getFormsListState({
        current: formsList,
        loading,
      }),
    [loading, formsList]
  );

  return (
    <PageLayout className="responsive-padding-x relative w-full h-full overflow-x-hidden">
      <section className="flex mb-6">
        <div className="flex flex-1 items-center">
          <h4
            className="text-neutral-shade-100"
            data-testid="work-package-header"
          >
            {formList.labelPlural}
          </h4>
          <Input
            containerClassName="hidden lg:flex lg:w-60 ml-6"
            placeholder={`Search ${formList.labelPlural}`}
            onChange={onChange}
            icon="search"
            data-testid="work-package-search"
          />
          {!isMobile && (
            <>
              <ButtonSecondary
                iconStart="filter"
                label={`Filters ${
                  totalFiltersSelected && totalFiltersSelected > 0
                    ? "(" + totalFiltersSelected + ")"
                    : ""
                }`}
                controlStateClass="text-base p-1.5"
                className="text-neutral-shade-100 flex-shrink-0 ml-6 h-[2.3rem]"
                onClick={toggleFilters}
              />
              <p className="ml-4">
                {formsList.length} / {formsListCount} results
              </p>
            </>
          )}
        </div>
        {displayAddForm && !isViewer() && (
          <Dropdown className="relative z-[11]" menuItems={[menuItems]}>
            <ButtonPrimary label="Add Form" iconEnd="chevron_big_down" />
          </Dropdown>
        )}
      </section>

      <Input
        containerClassName="lg:hidden mb-[13px]"
        placeholder={`Search ${formList.labelPlural.toLowerCase()}`}
        onChange={onChange}
        icon="search"
        data-testid="work-package-search"
      />
      {isMobile && (
        <div className="flex justify-end items-center gap-2 self-stretch text-[13px] font-light  ">
          <p className="ml-4 leading-[120%]">
            {formsList.length} / {formsListCount} results
          </p>
          <ButtonSecondary
            iconStart="filter"
            label={`Filters ${
              totalFiltersSelected && totalFiltersSelected > 0
                ? "(" + totalFiltersSelected + ")"
                : ""
            }`}
            controlStateClass="text-base p-1.5"
            className="text-neutral-shade-100 flex-shrink-0 ml-6 h-[2.3rem] sm:text-[16px] sm:font-semibold sm:leading-[130%]"
            onClick={toggleFilters}
          />
        </div>
      )}

      <div className="responsive-padding-y flex-1">
        {loading || formsList.length > 0 ? (
          <FormsList
            formsData={formsList}
            state={uiState}
            onLoadMore={() => onLoadMoreFormsList()}
            disableFetchMore={disableFetchMore}
          />
        ) : search || (totalFiltersSelected && totalFiltersSelected > 0) ? (
          <div className="w-full h-full lg:h-2/3 flex items-center justify-center">
            <EmptyContent
              title={`There are no ${formList.labelPlural.toLowerCase()} found`}
              description="based on the filters you've set. Try changing your filters."
            />
          </div>
        ) : (
          <div className="w-full h-full lg:h-2/3 flex items-center justify-center">
            <EmptyContent
              title={`You currently have no ${formList.labelPlural.toLowerCase()}`}
              description="If you believe this is an error, please contact your customer success manager to help troubleshoot the issues"
            />
          </div>
        )}
      </div>
      <FormFilters
        isOpen={showFilters}
        onClose={toggleFilters}
        onFiltersUpdate={handleFilterUpdate}
      />
    </PageLayout>
  );
}

export const getServerSideProps: GetServerSideProps = async context =>
  authGetServerSidePropsProxy(context, async () => {
    //TODO Needs to be revised when we switch to feature flags
    //https://urbint.atlassian.net/browse/WSAPP-1207
    const {
      data: { me },
    } = await authenticatedQuery(
      {
        query: TenantName,
      },
      context
    );

    const { displayFormsList, displayAddEbo, displayAddJsb, displayAddForm } =
      useTenantFeatures(me.tenant.name);

    if (!displayFormsList) {
      return {
        redirect: {
          permanent: false,
          destination: "/404",
        },
      };
    }
    return {
      props: {
        displayAddEbo: displayAddEbo,
        displayAddJsb: displayAddJsb,
        displayAddForm: displayAddForm,
      },
    };
  });
