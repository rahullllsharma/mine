import type {
  MultiOption,
  TemplatesListRequest,
} from "@/components/templatesComponents/customisedForm.types";
import type { GetServerSideProps } from "next";
import type {
  DraftFilter,
  FilterField,
  PublishedFilter,
} from "@/types/Templates/TemplateLists";
import React, { useContext, useEffect, useMemo, useReducer } from "react";
import { useRouter } from "next/router";
import { debounce, isArray } from "lodash";
import useRestMutation from "@/hooks/useRestMutation";
import { messages } from "@/locales/messages";
import {
  authenticatedQuery,
  authGetServerSidePropsProxy,
} from "@/graphql/client";
import { useTenantFeatures } from "@/hooks/useTenantFeatures";
import TenantName from "@/graphql/queries/tenantName.gql";
import Tabs from "@/components/shared/tabs/Tabs";
import { ListNavigationBar } from "@/components/templatesComponents/navigation/Navigation";
import Filters from "@/components/templatesComponents/listItems/Filters";
import TemplateList from "@/components/templatesComponents/listItems/TemplateList";
import Modals from "@/components/templatesComponents/listItems/Modals";
import axiosRest from "../../api/customFlowApi";
import PageLayout from "../../components/layout/pageLayout/PageLayout";
import ToastContext from "../../components/shared/toast/context/ToastContext";
import { convertToDateStringFormat } from "../../utils/date/helper";

const GET_TEMPLATES_LIST_LIMIT = 50;

type TemplateType = "published" | "draft";

export const publishedFilters: PublishedFilter[] = [
  {
    field: "TEMPLATENAME",
    values: [],
  },
  {
    field: "PUBLISHEDBY",
    values: [],
  },
  {
    field: "PUBLISHEDON",
    values: { from: null, to: null },
  },
];

export const draftFilters: DraftFilter[] = [
  {
    field: "TEMPLATENAME",
    values: [],
  },
  {
    field: "UPDATEDBY",
    values: [],
  },
  {
    field: "UPDATEDAT",
    values: { from: null, to: null },
  },
];

type State = {
  selectedTab: TemplateType;
  offset: {
    published: number;
    draft: number;
  };
  loading: boolean;
  allTemplates: {
    published: any[];
    draft: any[];
  };
  templates: {
    published: any[];
    draft: any[];
  };
  showFilters: boolean;
  showVersionHistory: boolean;
  showPublishModal: boolean;
  disableFetchMore: {
    published: boolean;
    draft: boolean;
  };
  filterCounts: { published: number; draft: number };
  searchValue: string;
  filterRequests: { published: PublishedFilter[]; draft: DraftFilter[] };
  selectedTemplateUUID: string;
  selectedTemplateTitle: string;
};

const defaultState = {
  filterRequests: {
    published: publishedFilters,
    draft: draftFilters,
  },
};

const initialState = (tab?: TemplateType): State => ({
  selectedTab: isTemplateType(tab) ? tab : "published",
  offset: {
    published: 0,
    draft: 0,
  },
  loading: true,
  allTemplates: {
    published: [],
    draft: [],
  },
  templates: {
    published: [],
    draft: [],
  },
  showFilters: false,
  showVersionHistory: false,
  showPublishModal: false,
  disableFetchMore: {
    published: false,
    draft: false,
  },
  filterCounts: { published: 0, draft: 0 },
  searchValue: "",
  filterRequests: defaultState.filterRequests,
  selectedTemplateUUID: "",
  selectedTemplateTitle: "",
});

const tabMapping = {
  published: 0,
  draft: 1,
};

const tabs: TemplateType[] = ["published", "draft"];

type Action =
  | { type: "SET_TAB"; payload: TemplateType }
  | { type: "SET_LOADING"; payload: boolean }
  | {
      type: "SET_TEMPLATES";
      payload: { templates: any[]; type: TemplateType; append?: boolean };
    }
  | { type: "TOGGLE_FILTER" }
  | {
      type: "TOGGLE_MODAL";
      payload: {
        type: "versionHistory" | "publish";
        value?: boolean;
        uuid?: string;
        templateTitle?: string;
      };
    }
  | {
      type: "UPDATE_SEARCH";
      payload: { searchValue: string };
    }
  | {
      type: "UPDATE_FILTER_REQUESTS";
      payload: { filters: any; type: TemplateType };
    }
  | {
      type: "UPDATE_FILTER_COUNTS";
      payload: { count: number; type: TemplateType };
    }
  | { type: "SET_OFFSET"; payload: { value: number; type: TemplateType } }
  | {
      type: "SET_DISABLE_FETCH_MORE";
      payload: { value: boolean; type: TemplateType };
    }
  | {
      type: "FILTER_CHANGE";
      payload: {
        type: TemplateType;
        filter: PublishedFilter | DraftFilter;
      };
    };

const getFilterCount = (filters: Array<PublishedFilter | DraftFilter>) => {
  return filters?.reduce?.((acc, filter) => {
    if (isArray(filter.values)) {
      return acc + filter.values.length;
    }
    return filter.values.from || filter.values.to ? acc + 1 : acc;
  }, 0);
};
const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case "SET_TAB":
      return {
        ...state,
        selectedTab: action.payload,
        offset: {
          ...state.offset,
          [action.payload]: 0,
        },
        loading: true,
      };
    case "SET_LOADING":
      return { ...state, loading: action.payload };

    case "SET_TEMPLATES":
      return {
        ...state,
        templates: {
          ...state.templates,
          [action.payload.type]: action.payload.append
            ? [
                ...state.templates[action.payload.type],
                ...action.payload.templates,
              ]
            : action.payload.templates,
        },
        disableFetchMore: {
          ...state.disableFetchMore,
          [action.payload.type]:
            action.payload.templates.length < GET_TEMPLATES_LIST_LIMIT,
        },
      };
    case "TOGGLE_FILTER":
      return {
        ...state,
        showFilters: !state.showFilters,
      };
    case "TOGGLE_MODAL":
      return {
        ...state,
        showVersionHistory:
          action.payload.type === "versionHistory"
            ? !state.showVersionHistory
            : state.showVersionHistory,
        showPublishModal:
          action.payload.type === "publish"
            ? !state.showPublishModal
            : state.showPublishModal,
        selectedTemplateUUID: action.payload.uuid || state.selectedTemplateUUID,
        selectedTemplateTitle:
          action.payload.templateTitle || state.selectedTemplateTitle,
      };
    case "UPDATE_SEARCH":
      return {
        ...state,
        searchValue: action.payload.searchValue,
      };
    case "UPDATE_FILTER_REQUESTS":
      return {
        ...state,
        filterRequests: {
          ...state.filterRequests,
          [action.payload.type]: action.payload.filters,
        },
      };
    case "UPDATE_FILTER_COUNTS":
      return {
        ...state,
        filterCounts: {
          ...state.filterCounts,
          [state.selectedTab]: action.payload.count,
        },
      };
    case "SET_OFFSET":
      return {
        ...state,
        offset: {
          ...state.offset,
          [action.payload.type]: action.payload.value,
        },
      };
    case "SET_DISABLE_FETCH_MORE":
      return {
        ...state,
        disableFetchMore: {
          ...state.disableFetchMore,
          [action.payload.type]: action.payload.value,
        },
      };
    case "FILTER_CHANGE":
      return {
        ...state,
        filterRequests: {
          ...state.filterRequests,
          [action.payload.type]: state.filterRequests[action.payload.type].map(
            filter =>
              filter.field === action.payload.filter.field
                ? action.payload.filter
                : filter
          ),
        },
      };
    default:
      return state;
  }
};

const isTemplateType = (value: any): value is TemplateType => {
  return tabs.includes(value);
};

export const getFilterField = (
  filters: Array<PublishedFilter | DraftFilter>,
  type: FilterField
): MultiOption[] => {
  const field = filters.find(filter => filter.field === type);
  if (field && isArray(field?.values)) {
    return field.values;
  }
  return [];
};

export const getDateFilterField = (
  filters: Array<PublishedFilter | DraftFilter>,
  type: FilterField
): { from: Date | null; to: Date | null } => {
  const field = filters.find(filter => filter.field === type);
  if (field && !isArray(field?.values)) {
    return field.values;
  }
  return { from: null, to: null };
};

const getFiltersApiPayload = (
  filters: { published: PublishedFilter[]; draft: DraftFilter[] },
  type: TemplateType
) => {
  if (type === "published") {
    const dateFilter = getDateFilterField(filters.published, "PUBLISHEDON");
    return {
      template_names: getFilterField(filters.published, "TEMPLATENAME").map(
        v => v.name
      ),
      published_by: getFilterField(filters.published, "PUBLISHEDBY").map(
        v => v.name
      ),
      published_at_start_date: dateFilter.from
        ? convertToDateStringFormat(new Date(dateFilter.from))
        : null,
      published_at_end_date: dateFilter.to
        ? convertToDateStringFormat(new Date(dateFilter.to))
        : null,
      orderBy: {
        field: "published_at",
        desc: true,
      },
    };
  }
  if (type === "draft") {
    const dateFilter = getDateFilterField(filters.draft, "UPDATEDAT");
    return {
      template_names: getFilterField(filters.draft, "TEMPLATENAME").map(
        v => v.name
      ),
      updated_by: getFilterField(filters.draft, "UPDATEDBY").map(v => v.name),
      updated_at_start_date: dateFilter.from
        ? convertToDateStringFormat(new Date(dateFilter.from))
        : null,
      updated_at_end_date: dateFilter.to
        ? convertToDateStringFormat(new Date(dateFilter.to))
        : null,
      orderBy: {
        field: "updated_at",
        desc: true,
      },
    };
  }
  return {};
};

const debouncedFunction = debounce(
  (func: (...args: any) => void, ...args: any) => {
    func(...args);
  },
  500
);

const TemplatesListPage = (): JSX.Element => {
  const router = useRouter();
  const { tab } = router.query || "";
  const [state, dispatch] = useReducer(
    reducer,
    initialState(tab as TemplateType)
  );
  const toastCtx = useContext(ToastContext);
  const isInitialMount = React.useRef(true);
  const isFetchingRef = React.useRef(false);

  useEffect(() => {
    if (!isInitialMount.current && isTemplateType(tab)) {
      dispatch({ type: "SET_TAB", payload: tab });
    }
    isInitialMount.current = false;
  }, [tab]);

  // Fetch data only when tab changes or on initial mount
  useEffect(() => {
    fetchDataForSelectedTab(state);
  }, [state.selectedTab]);

  useEffect(() => {
    isFetchingRef.current = false;
  }, [state.selectedTab]);

  useEffect(() => {
    return () => {
      isFetchingRef.current = false;
    };
  }, []);

  const handleSearchChange = (
    dispatchFn: React.Dispatch<Action>,
    searchValue: string,
    currentState: State,
    fetchDataForSelectedTab: (state: State) => void
  ) => {
    dispatchFn({ type: "UPDATE_SEARCH", payload: { searchValue } });
    dispatchFn({
      type: "SET_OFFSET",
      payload: {
        value: 0,
        type: currentState.selectedTab,
      },
    });

    isFetchingRef.current = false;

    const updatedState: State = {
      ...currentState,
      searchValue,
      offset: {
        ...currentState.offset,
        [currentState.selectedTab]: 0,
      },
    };

    try {
      debouncedFunction(() => fetchDataForSelectedTab(updatedState));
    } catch (error) {
      toastCtx?.pushToast("error", messages.SomethingWentWrong);
    }
  };

  const toggleFilterPanel = () => {
    dispatch({ type: "TOGGLE_FILTER" });
  };
  const toggleVersionHistoryModal = (templateUUID = "", templateTitle = "") => {
    dispatch({
      type: "TOGGLE_MODAL",
      payload: {
        type: "versionHistory",
        uuid: templateUUID,
        templateTitle: templateTitle,
      },
    });
  };

  const togglePublishTemplateModal = (id?: string) => {
    dispatch({ type: "TOGGLE_MODAL", payload: { type: "publish", uuid: id } });
  };

  const { mutate: fetchTemplatesList } = useRestMutation<any>({
    endpoint: "/templates/list/",
    method: "post",
    axiosInstance: axiosRest,
    dtoFn: data => data,
    mutationOptions: {
      onError: () => {
        toastCtx?.pushToast("error", messages.SomethingWentWrong);
        dispatch({ type: "SET_LOADING", payload: false });
        isFetchingRef.current = false;
      },
      onSuccess: (data: any) => {
        try {
          dispatch({
            type: "SET_TEMPLATES",
            payload: {
              templates:
                state.offset[state.selectedTab] === 0
                  ? data?.data?.data
                  : [
                      ...state.templates[state.selectedTab],
                      ...data?.data?.data,
                    ],
              type: state.selectedTab,
              append: state.offset[state.selectedTab] > 0,
            },
          });
          dispatch({
            type: "SET_DISABLE_FETCH_MORE",
            payload: {
              value: data?.data?.data?.length < GET_TEMPLATES_LIST_LIMIT,
              type: state.selectedTab,
            },
          });
          dispatch({
            type: "SET_OFFSET",
            payload: {
              value: state.offset[state.selectedTab] + GET_TEMPLATES_LIST_LIMIT,
              type: state.selectedTab,
            },
          });
          dispatch({ type: "SET_LOADING", payload: false });
        } catch (error) {
          toastCtx?.pushToast("error", messages.SomethingWentWrong);
          dispatch({ type: "SET_LOADING", payload: false });
        } finally {
          isFetchingRef.current = false;
        }
      },
    },
  });

  const fetchDataForSelectedTab = async (newState: State) => {
    if (isFetchingRef.current) {
      return;
    }

    try {
      isFetchingRef.current = true;

      const filterKey =
        newState.selectedTab === "published"
          ? "publishedFilters"
          : "draftFilters";

      const storedFilters = localStorage.getItem(filterKey);
      const filters = storedFilters
        ? JSON.parse(storedFilters)
        : newState.filterRequests[newState.selectedTab];

      const requestData: TemplatesListRequest = {
        limit: GET_TEMPLATES_LIST_LIMIT,
        offset: newState.offset[newState.selectedTab],
        template_status: [newState.selectedTab],
        search:
          newState.searchValue.length > 0 ? newState.searchValue : undefined,
        ...getFiltersApiPayload(
          { ...newState.filterRequests, [newState.selectedTab]: filters },
          newState.selectedTab
        ),
      };

      dispatch({ type: "SET_LOADING", payload: true });

      fetchTemplatesList({
        ...requestData,
        append: newState.offset[newState.selectedTab] > 0,
      });
    } catch (error) {
      console.error("Error in fetchDataForSelectedTab:", error);
      toastCtx?.pushToast("error", messages.SomethingWentWrong);
      dispatch({ type: "SET_LOADING", payload: false });
      isFetchingRef.current = false;
    }
  };

  useEffect(() => {
    const filterKey =
      state.selectedTab === "published" ? "publishedFilters" : "draftFilters";

    const storedFilters = localStorage.getItem(filterKey);

    if (storedFilters) {
      const parsedFilters = JSON.parse(storedFilters);

      dispatch({
        type: "UPDATE_FILTER_REQUESTS",
        payload: {
          filters: parsedFilters,
          type: state.selectedTab,
        },
      });

      dispatch({
        type: "UPDATE_FILTER_COUNTS",
        payload: {
          count: getFilterCount(parsedFilters),
          type: state.selectedTab,
        },
      });
    }
  }, [state.selectedTab]);

  const onApplyFilters = (filters: Array<PublishedFilter | DraftFilter>) => {
    const filterKey =
      state.selectedTab === "published" ? "publishedFilters" : "draftFilters";

    // First update the filter requests in state
    dispatch({
      type: "UPDATE_FILTER_REQUESTS",
      payload: {
        filters: filters,
        type: state.selectedTab,
      },
    });

    // Save to localStorage
    localStorage.setItem(filterKey, JSON.stringify(filters));

    // Update filter counts
    dispatch({
      type: "UPDATE_FILTER_COUNTS",
      payload: {
        count: getFilterCount(filters),
        type: state.selectedTab,
      },
    });

    // Reset offset
    dispatch({
      type: "SET_OFFSET",
      payload: {
        value: 0,
        type: state.selectedTab,
      },
    });

    // Create new state with updated filters and reset offset
    const newState = {
      ...state,
      filterRequests: {
        ...state.filterRequests,
        [state.selectedTab]: filters,
      },
      offset: {
        ...state.offset,
        [state.selectedTab]: 0,
      },
    };

    // Fetch data with new state
    fetchDataForSelectedTab(newState);
    toggleFilterPanel();
  };

  // state change when loading
  const uiState = useMemo(() => {
    return state.loading ? "loading" : undefined;
  }, [state.loading]);

  // fetch draft templates details through get api
  const { mutate: changeTemplateToPublish } = useRestMutation<any>({
    endpoint: `/templates/${state.selectedTemplateUUID}`,
    method: "get",
    axiosInstance: axiosRest,
    dtoFn: data => data,
    mutationOptions: {
      onError: (error: any) => {
        console.log(error);
        toastCtx?.pushToast("error", messages.SomethingWentWrong);
      },
      onSuccess: (responseData: any) => {
        const {
          contents,
          properties,
          pre_population_rule_paths,
          settings,
          metadata,
        } = responseData.data;

        const updateReq = {
          contents: [...contents],
          properties: {
            ...properties,
            status: "published",
          },
          pre_population_rule_paths: pre_population_rule_paths
            ? { ...pre_population_rule_paths }
            : null,
          settings: settings ? { ...settings } : {},
          metadata: metadata ? { ...metadata } : {},
        };

        updateTemplateById(updateReq);
      },
    },
  });

  // Update the template status to publish once details are fetched.
  const { mutate: updateTemplateById } = useRestMutation<any>({
    endpoint: `/templates/${state.selectedTemplateUUID}`,
    method: "put",
    axiosInstance: axiosRest,
    dtoFn: data => data,
    mutationOptions: {
      onError: (error: any) => {
        console.log(error);
        toastCtx?.pushToast("error", messages.SomethingWentWrong);
      },
      onSuccess: (data: any) => {
        const transformedData = {
          ...data,
          properties: {
            ...data.properties,
            status: "published",
          },
        };
        toastCtx?.pushToast("success", "Your template has been published");
        router.push("/templates");
        dispatch({ type: "SET_TAB", payload: "published" });
        return transformedData;
      },
    },
  });

  const publishTemplate = () => {
    changeTemplateToPublish({});
    dispatch({
      type: "TOGGLE_MODAL",
      payload: { type: "publish", value: false },
    });
  };

  const deduplicateTemplates = (templates: any[]) => {
    const uniqueTemplates = new Map();
    templates.forEach(template => {
      uniqueTemplates.set(template.id, template);
    });
    return Array.from(uniqueTemplates.values());
  };

  return (
    <PageLayout className="responsive-padding-x relative w-full h-full overflow-x-hidden">
      <ListNavigationBar
        toggleFilters={toggleFilterPanel}
        totalFilterSelected={state.filterCounts[state.selectedTab]}
        onSearchChange={event =>
          handleSearchChange(
            dispatch,
            event.target.value,
            state,
            fetchDataForSelectedTab
          )
        }
        searchValue={state.searchValue}
      />
      <Tabs
        itemClasses={{
          default:
            "text-neutral-shade-75 font-semibold active:bg-neutral-shade-3 border-b-4",
          selected: "border-brand-urbint-40 border-solid z-10",
          unselected: "opacity-75 border-transparent",
        }}
        options={["Published", "Draft"]}
        defaultIndex={tabMapping[state.selectedTab]}
        onSelect={(index: number) =>
          dispatch({ type: "SET_TAB", payload: tabs[index] })
        }
      />
      <hr
        className="relative bg-neutral-shade-18 z-1 border"
        style={{
          bottom: "3px",
        }}
      />
      <Filters
        data={state.templates[state.selectedTab]}
        isOpen={state.showFilters}
        onClose={toggleFilterPanel}
        onApply={onApplyFilters}
        filtersValues={state.filterRequests[state.selectedTab]}
        type={state.selectedTab}
        onClear={() => {
          dispatch({
            type: "UPDATE_FILTER_REQUESTS",
            payload: {
              filters: defaultState.filterRequests[state.selectedTab],
              type: state.selectedTab,
            },
          });
        }}
        onChangeFilter={(filter: PublishedFilter | DraftFilter) =>
          dispatch({
            type: "FILTER_CHANGE",
            payload: {
              type: state.selectedTab,
              filter,
            },
          })
        }
      />
      <TemplateList
        selectedTab={tabMapping[state.selectedTab]}
        state={uiState}
        publishedTemplates={deduplicateTemplates(state.templates.published)}
        draftTemplates={deduplicateTemplates(state.templates.draft)}
        disableFetchMore={state.disableFetchMore[state.selectedTab]}
        loadMoreTemplates={() => fetchDataForSelectedTab(state)}
        togglePublishTemplateModal={(templateUUID?: string) =>
          togglePublishTemplateModal(templateUUID)
        }
        toggleVersionHistoryModal={toggleVersionHistoryModal}
      />
      <Modals
        showVersionHistory={state.showVersionHistory}
        showPublishModal={state.showPublishModal}
        togglePublishTemplateModal={togglePublishTemplateModal}
        toggleVersionHistoryModal={toggleVersionHistoryModal}
        selectedTemplateUUID={state.selectedTemplateUUID}
        publishTemplate={publishTemplate}
        selectedTemplateTitle={state.selectedTemplateTitle}
      />
    </PageLayout>
  );
};

export default TemplatesListPage;

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

    const { displayTemplatesList } = useTenantFeatures(me.tenant.name);

    if (!displayTemplatesList) {
      return {
        redirect: {
          permanent: false,
          destination: "/404",
        },
      };
    }
    return { props: {} };
  });
