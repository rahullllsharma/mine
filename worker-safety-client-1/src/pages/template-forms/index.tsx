import type { GetServerSideProps } from "next";
import type { ChangeEvent } from "react";
import type { TemplateFormsListRequest } from "@/components/templatesComponents/customisedForm.types";
import type { TemplateFormsFilter } from "@/components/templatesComponents/filter/TemplateFormFilters";
import { debounce } from "lodash-es";
import router from "next/router";
import { useContext, useEffect, useMemo, useState } from "react";
import axiosRest from "@/api/restApi";
import EmptyContent from "@/components/emptyContent/EmptyContent";
import PageLayout from "@/components/layout/pageLayout/PageLayout";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import TemplateFormListHeader from "@/components/templatesComponents/TemplateForms/TemplateFormListHeader";
import { TemplateFormsList } from "@/components/templatesComponents/TemplateForms/TemplateFormsList";
import { useTemplateFormsFilterContext } from "@/components/templatesComponents/context/TemplateFormsFiltersProvider";
import TemplateFormFilters from "@/components/templatesComponents/filter/TemplateFormFilters";
import { config } from "@/config";
import TenantName from "@/graphql/queries/tenantName.gql";
import { messages } from "@/locales/messages";
import { convertToDateStringFormat } from "@/utils/date/helper";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import {
  authenticatedQuery,
  authGetServerSidePropsProxy,
} from "@/graphql/client";
import useRestMutation from "@/hooks/useRestMutation";
import { useTenantFeatures } from "@/hooks/useTenantFeatures";
import { useInfiniteScroll } from "@/components/templatesComponents/Scroll/useInfiniteScroll";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import Loader from "../../components/shared/loader/Loader";

const ShimmerRow = () => (
  <div className="animate-pulse w-full h-20 bg-neutral-10 rounded mb-2" />
);

function TemplateListForms() {
  const toastCtx = useContext(ToastContext);
  const PAGE_SIZE = 50;
  const [offset, setOffset] = useState(0);
  const [templateFormsData, setTemplateFormsData] = useState<any[]>([]);
  const { filters: defaultFilters } = useTemplateFormsFilterContext();
  const { getCwfTemplateFormFilters } = useAuthStore();
  const preferenceFilters = getCwfTemplateFormFilters() ?? defaultFilters;

  const [totalFilterSelected, setTotalFilterSelected] = useState<number>(
    preferenceFilters.filter(f => f.values.length > 0).length
  );
  const [showFilters, setShowFilters] = useState(false);
  const [resultsCount, setResultsCount] = useState<number | null>(null);
  const [totalFormsCount, setTotalFormsCount] = useState<number | null>(null);

  const { getAllEntities } = useTenantStore();
  const { templateForm } = getAllEntities();

  const [isInitialLoading, setInitialLoading] = useState(true);
  const [isFetchingMore, setFetchingMore] = useState(false);
  const [disableFetchMore, setDisableFetchMore] = useState(false);

  const convertRequestBody = (
    filterValues: TemplateFormsFilter[]
  ): TemplateFormsListRequest => {
    const getByName = (field: string) =>
      filterValues.find(f => f.field === field)?.values.map(v => v.name) || [];
    const getById = (field: string) =>
      filterValues.find(f => f.field === field)?.values.map(v => v.id) || [];

    const req: TemplateFormsListRequest = {
      form_names: getByName("FORMNAME"),
      offset,
      limit: PAGE_SIZE,
      status: getById("STATUS"),
      updated_at_start_date: getByName("UPDATEDON")[0]
        ? convertToDateStringFormat(new Date(getByName("UPDATEDON")[0]))
        : null,
      updated_at_end_date: getByName("UPDATEDON")[1]
        ? convertToDateStringFormat(new Date(getByName("UPDATEDON")[1]))
        : null,
      created_at_start_date: getByName("CREATEDON")[0]
        ? convertToDateStringFormat(new Date(getByName("CREATEDON")[0]))
        : null,
      created_at_end_date: getByName("CREATEDON")[1]
        ? convertToDateStringFormat(new Date(getByName("CREATEDON")[1]))
        : null,
      updated_by: getByName("UPDATEDBY"),
      created_by: getByName("CREATEDBY"),
      completed_at_start_date: getByName("COMPLETEDON")[0]
        ? convertToDateStringFormat(new Date(getByName("COMPLETEDON")[0]))
        : null,
      completed_at_end_date: getByName("COMPLETEDON")[1]
        ? convertToDateStringFormat(new Date(getByName("COMPLETEDON")[1]))
        : null,
      work_package_id: getById("WORKPACKAGE"),
      location_id: getById("LOCATION"),
      region_id: getById("REGION"),
      reported_at_start_date: getByName("REPORTEDON")[0]
        ? convertToDateStringFormat(new Date(getByName("REPORTEDON")[0]))
        : null,
      reported_at_end_date: getByName("REPORTEDON")[1]
        ? convertToDateStringFormat(new Date(getByName("REPORTEDON")[1]))
        : null,
      supervisor_id: getById("SUPERVISOR"),
    };

    setTotalFilterSelected(
      filterValues.filter(f => f.values.length > 0).length
    );
    return req;
  };

  const uiState = useMemo(() => {
    if (isInitialLoading) return "loading";
    return undefined;
  }, [isInitialLoading]);

  const [requestData, setRequestData] = useState<TemplateFormsListRequest>(() =>
    convertRequestBody(preferenceFilters)
  );

  const { mutate: fetchTemplateForms } = useRestMutation<any>({
    endpoint: `${config.workerSafetyCustomWorkFlowUrlRest}/forms/list/`,
    method: "post",
    axiosInstance: axiosRest,
    dtoFn: d => d,
    mutationOptions: {
      onSuccess: (res: any) => {
        setResultsCount(res.data.metadata?.count || 0);

        setTemplateFormsData(prev => {
          const list =
            offset === 0 ? res.data.data : [...prev, ...res.data.data];

          const done = list.length >= res.data.metadata.count;
          setDisableFetchMore(done);

          return list;
        });

        setInitialLoading(false);
        setFetchingMore(false);
      },

      onError: () => {
        setInitialLoading(false);
        setFetchingMore(false);
        toastCtx?.pushToast("error", messages.SomethingWentWrong);
      },
    },
  });

  const { mutate: fetchTotalFormsCount } = useRestMutation<any>({
    endpoint: `${config.workerSafetyCustomWorkFlowUrlRest}/forms/list/`,
    method: "post",
    axiosInstance: axiosRest,
    dtoFn: () => ({
      offset: 0,
      limit: 1,
      search: "",
      filters: [],
    }),
    mutationOptions: {
      onSuccess: (res: any) => {
        setTotalFormsCount(res.data.metadata?.count || 0);
      },
      onError: () => {
        console.error("Failed to fetch total forms count");
      },
    },
  });

  useEffect(() => {
    fetchTemplateForms(requestData);
    fetchTotalFormsCount({});
  }, [requestData]);
  const loadMore = () => {
    if (disableFetchMore) return;
    setFetchingMore(true);
    setOffset(prevOffset => {
      const next = prevOffset + PAGE_SIZE;
      setRequestData(prev => ({ ...prev, offset: next }));
      return next;
    });
  };
  const sentinelRef = useInfiniteScroll(
    loadMore,
    isFetchingMore,
    !disableFetchMore
  );

  const onToggleFilter = () => setShowFilters(p => !p);

  const onChangeInput = debounce((e: ChangeEvent<HTMLInputElement>) => {
    setOffset(0);
    setRequestData(prev => ({
      ...prev,
      search: e.target.value,
      offset: 0,
    }));
  }, 300);

  const onFiltersApply = (values: TemplateFormsFilter[]) => {
    setOffset(0);
    setRequestData({
      ...convertRequestBody(values),
      offset: 0,
      limit: PAGE_SIZE,
    });
    onToggleFilter();
  };

  return (
    <PageLayout className="responsive-padding-x relative w-full h-full overflow-x-hidden">
      <TemplateFormListHeader
        pageTitle={templateForm?.labelPlural}
        inputPlaceHolder={`Search ${templateForm?.labelPlural}`}
        toggleFilters={onToggleFilter}
        totalFilterSelected={totalFilterSelected}
        resultsCount={resultsCount}
        totalFormsCount={totalFormsCount}
        onChange={onChangeInput}
      />

      <div className="responsive-padding-y flex-1">
        {templateFormsData.length ? (
          <>
            <TemplateFormsList
              // eslint-disable-next-line @typescript-eslint/no-empty-function
              onLoadMore={() => {}}
              state={uiState}
              onView={id => router.push("/templates/view?templateId=" + id)}
              templateFormsData={templateFormsData}
              disableFetchMore={disableFetchMore}
            />
            <div ref={sentinelRef} />
            {isFetchingMore && (
              <div className="my-4 px-4">
                {[...Array(3)].map((_, i) => (
                  <ShimmerRow key={i} />
                ))}
              </div>
            )}
          </>
        ) : // eslint-disable-next-line no-negated-condition
        !isInitialLoading ? (
          <div className="w-full h-full lg:h-2/3 flex items-center justify-center">
            <EmptyContent
              title="No results found"
              description="Try adjusting your search or filter options"
            />
          </div>
        ) : (
          <Loader />
        )}

        <TemplateFormFilters
          isOpen={showFilters}
          css="z-30"
          onClose={onToggleFilter}
          onFiltersApply={onFiltersApply}
        />
      </div>
    </PageLayout>
  );
}

export default TemplateListForms;

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

    const { displayTemplateFormsList } = useTenantFeatures(me.tenant.name);
    if (!displayTemplateFormsList) {
      return {
        redirect: {
          permanent: false,
          destination: "/404",
        },
      };
    }
    return { props: {} };
  });
