import type { MultiOption } from "../../filters/multiOptionWrapper/MultiOptionWrapper";
import type { FormsListFilterOptions } from "@/types/formsList/formsList";
import type { UserPreferenceFormFilters } from "@/types/auth/AuthUser";
import {
  useContext,
  useReducer,
  useEffect,
  useRef,
  useState,
  useCallback,
} from "react";
import { useMutation, useQuery } from "@apollo/client";
import gql from "graphql-tag";
import debounce from "lodash/debounce";
import { BodyText } from "@urbint/silica";
import MultiSelect from "@/components/shared/inputSelect/multiSelect/MultiSelect";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import Flyover from "@/components/flyover/Flyover";
import ButtonTertiary from "@/components/shared/button/tertiary/ButtonTertiary";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import SaveFormFiltersMutation from "@/pages/forms/SaveFormFilters.mutation.gql";
import GetFormsListFilterOptions from "@/graphql/queries/GetFormsListFilterOptions.gql";
import { formatCamelCaseString } from "@/utils/date/helper";
import { Toggle } from "@/components/forms/Basic/Toggle";
import InputDateSelect from "@/components/shared/inputDateSelect/InputDateSelect";
import { getTenantName } from "@/components/forms/Ebo/TenantLabel/LabelOnBasisOfTenant";
import { CircularLoader } from "@/components/uploadLoader/uploadLoader";
import { sessionExpiryHandlerForApolloClient } from "@/utils/auth";
import MultiOptionWrapper from "../../filters/multiOptionWrapper/MultiOptionWrapper";
import FilterSection from "../FilterSection";
import LoadingFiltersComponent from "./LoadingFiltersComponent";
import InputWithChips from "./InputWithChip";

export type FormFiltersProps = {
  isOpen: boolean;
  onClose: () => void;
  onFiltersUpdate: (filters: FormFilter[]) => void;
};
type CreatedByUser = {
  id: string;
  name: string;
};

type UpdatedByUser = {
  id: string;
  name: string;
};

interface UpdatedByState {
  searchQuery: string;
  offset: number;
  loading: boolean;
  users: UpdatedByUser[];
  hasMore: boolean;
  originalUsers: UpdatedByUser[];
  localValue: string;
}

type UpdatedByAction =
  | { type: "SET_SEARCH_QUERY"; payload: string }
  | { type: "SET_OFFSET"; payload: number }
  | { type: "SET_LOADING"; payload: boolean }
  | { type: "SET_USERS"; payload: UpdatedByUser[] }
  | { type: "APPEND_USERS"; payload: UpdatedByUser[] }
  | { type: "SET_HAS_MORE"; payload: boolean }
  | { type: "SET_ORIGINAL_USERS"; payload: UpdatedByUser[] }
  | { type: "SET_LOCAL_VALUE"; payload: string }
  | { type: "RESET" };

const initialUpdatedByState: UpdatedByState = {
  searchQuery: "",
  offset: 0,
  loading: false,
  users: [],
  hasMore: true,
  originalUsers: [],
  localValue: "",
};

function updatedByReducer(
  state: UpdatedByState,
  action: UpdatedByAction
): UpdatedByState {
  switch (action.type) {
    case "SET_SEARCH_QUERY":
      return { ...state, searchQuery: action.payload };
    case "SET_OFFSET":
      return { ...state, offset: action.payload };
    case "SET_LOADING":
      return { ...state, loading: action.payload };
    case "SET_USERS":
      return { ...state, users: action.payload };
    case "APPEND_USERS":
      return { ...state, users: [...state.users, ...action.payload] };
    case "SET_HAS_MORE":
      return { ...state, hasMore: action.payload };
    case "SET_ORIGINAL_USERS":
      return { ...state, originalUsers: action.payload };
    case "SET_LOCAL_VALUE":
      return { ...state, localValue: action.payload };
    case "RESET":
      return initialUpdatedByState;
    default:
      return state;
  }
}

const GET_FORMS_LIST_FILTER_OPTIONS_CREATED_BY_USERS = gql`
  query GetFormsListFilterOptionsCreatedByUsers(
    $limit: Int
    $offset: Int
    $filterSearch: FormListFilterSearchInput
  ) {
    formsListFilterOptions(
      limit: $limit
      offset: $offset
      filterSearch: $filterSearch
    ) {
      createdByUsers {
        id
        name
      }
    }
  }
`;

const GET_FORMS_LIST_FILTER_OPTIONS_UPDATED_BY_USERS = gql`
  query GetFormsListFilterOptionsUpdatedByUsers(
    $limit: Int
    $offset: Int
    $filterSearch: FormListFilterSearchInput
  ) {
    formsListFilterOptions(
      limit: $limit
      offset: $offset
      filterSearch: $filterSearch
    ) {
      updatedByUsers {
        id
        name
      }
    }
  }
`;

type FilterField =
  | "FORM"
  | "LOCATIONS"
  | "STATUS"
  | "FORMID"
  | "WORKPACKAGE"
  | "CREATEDBY"
  | "CREATEDON"
  | "UPDATEDBY"
  | "UPDATEDON"
  | "COMPLETEDON"
  | "REPORTDATE"
  | "OPERATINGHQ"
  | "SUPERVISOR";

export type FormFilter = {
  field: FilterField;
  values: MultiOption[];
};

const formStatusForNg = ["asgard", "urbint-integration", "test-ng", "ng"];

const DEFAULT_FILTERS: FormFilter[] = [
  { field: "STATUS", values: [] },
  { field: "FORM", values: [] },
  { field: "FORMID", values: [] },
  { field: "WORKPACKAGE", values: [] },
  { field: "CREATEDBY", values: [] },
  { field: "CREATEDON", values: [] },
  { field: "UPDATEDBY", values: [] },
  { field: "UPDATEDON", values: [] },
  { field: "LOCATIONS", values: [] },
  { field: "COMPLETEDON", values: [] },
  { field: "REPORTDATE", values: [] },
  { field: "OPERATINGHQ", values: [] },
  { field: "SUPERVISOR", values: [] },
];

enum StatusLevel {
  IN_PROGRESS = "In-Progress",
  COMPLETE = "Complete",
  PENDING_POST_JOB_BRIEF = "Pending Post Job Brief",
  PENDING_SIGN_OFF = "Pending Sign Off",
}

export default function FormFilters({
  isOpen,
  onClose,
  onFiltersUpdate,
}: FormFiltersProps): JSX.Element {
  const DEBOUNCE_TIME = 500;
  const createdByFlagRef = useRef(true);
  const updatedByFlagRef = useRef(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [offset, setOffset] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [createdByUsers, setCreatedByUsers] = useState<CreatedByUser[]>([]);
  const [hasMore, setHasMore] = useState(true);
  const [localValue, setLocalValue] = useState("");
  const [tenantName, setTenantName] = useState<string>("");
  const [originalCreatedByUsers, setOriginalCreatedByUsers] = useState<
    CreatedByUser[]
  >([]);

  const [updatedByState, dispatch] = useReducer(
    updatedByReducer,
    initialUpdatedByState
  );

  const toastCtx = useContext(ToastContext);

  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const scrollContainerRefUpdatedBy = useRef<HTMLDivElement>(null);

  const DEFAULT_LIMIT = 1000;
  const scrollPositionRef = useRef(0);
  const scrollPositionRefForUpdatedBy = useRef(0);

  const debouncedUpdateSearch = useRef(
    debounce((value: string) => {
      setSearchQuery(value);
      setOffset(0);
      setCreatedByUsers([]);
    }, DEBOUNCE_TIME)
  ).current;

  const debouncedUpdatedBySearch = useRef(
    debounce((value: string) => {
      dispatch({ type: "SET_SEARCH_QUERY", payload: value });
      dispatch({ type: "SET_OFFSET", payload: 0 });
      dispatch({ type: "SET_USERS", payload: [] });
    }, DEBOUNCE_TIME)
  ).current;

  const { me, getFormFilters, setUser } = useAuthStore();
  const { formList } = useTenantStore(state => state.getAllEntities());

  const [applyFiltersDisabled, setApplyFiltersDisabled] =
    useState<boolean>(true);
  const [formFilters, setFormFilters] = useState<FormFilter[]>(DEFAULT_FILTERS);
  const [createdOnFromDate, setCreatedOnFromDate] = useState<Date | null>(null);
  const [createdOnToDate, setCreatedOnToDate] = useState<Date | null>(null);
  const [updatedOnFromDate, setUpdatedOnFromDate] = useState<Date | null>(null);
  const [updatedOnToDate, setUpdatedOnToDate] = useState<Date | null>(null);
  const [completedOnFromDate, setCompletedOnFromDate] = useState<Date | null>(
    null
  );
  const [completedOnToDate, setCompletedOnToDate] = useState<Date | null>(null);
  const [reportDateFromDate, setReportDateFromDate] = useState<Date | null>(
    null
  );
  const [reportDateToDate, setReportDateToDate] = useState<Date | null>(null);

  const [saveFormFiltersMutation] = useMutation(SaveFormFiltersMutation);

  const { data: { formsListFilterOptions } = {}, loading } = useQuery<{
    formsListFilterOptions: FormsListFilterOptions;
  }>(GetFormsListFilterOptions, {
    onError: _err => {
      sessionExpiryHandlerForApolloClient(_err);
      toastCtx?.pushToast("error", "Error fetching form filters options");
    },
  });

  const changeDisplayNameNotation = (formId: string) => {
    if (formId === "NatGridJobSafetyBriefing") {
      return "Distribution Job Safety Briefing";
    } else {
      return formatCamelCaseString(formId);
    }
  };

  const formIdOptions =
    formsListFilterOptions?.formNames.map(formId => ({
      id: formId,
      name: changeDisplayNameNotation(formId),
    })) || [];

  const idOptions =
    formsListFilterOptions?.formIds.map(id => ({
      id,
      name: id,
    })) || [];

  const locationsOption = formsListFilterOptions?.locations || [];
  const supervisorOption = formsListFilterOptions?.supervisors || [];

  const operatingHqOptions =
    formsListFilterOptions?.operatingHqs.map(hq => ({
      id: hq,
      name: hq,
    })) || [];

  type FilterType =
    | "CREATEDON"
    | "UPDATEDON"
    | "UPDATEDON"
    | "COMPLETEDON"
    | "REPORTDATE";

  const handleDateChange = (
    date: Date | null,
    setDate: (date: Date | null) => void,
    filterType?: FilterType
  ) => {
    setDate(date);
    if (!date && filterType) {
      filterUpdateHandler([], filterType);
    }
  };

  const handleCreatedOnFormDateChange = (date: Date | null) => {
    handleDateChange(date, setCreatedOnFromDate, "CREATEDON");
    setCreatedOnToDate(new Date());
  };

  const handleCreatedOnToDateChange = (date: Date | null) =>
    handleDateChange(date, setCreatedOnToDate);

  const handleUpdatedOnFromDateChange = (date: Date | null) => {
    handleDateChange(date, setUpdatedOnFromDate, "UPDATEDON");
    setUpdatedOnToDate(new Date());
  };

  const handleUpdatedToDateChange = (date: Date | null) =>
    handleDateChange(date, setUpdatedOnToDate);

  const handleCompletedOnFromDateChange = (date: Date | null) => {
    handleDateChange(date, setCompletedOnFromDate, "COMPLETEDON");
    setCompletedOnToDate(new Date());
  };

  const handleCompletedOnToDateChange = (date: Date | null) =>
    handleDateChange(date, setCompletedOnToDate);

  const handleReportDateFromDateChange = (date: Date | null) => {
    handleDateChange(date, setReportDateFromDate, "REPORTDATE");
    setReportDateToDate(new Date());
  };

  const handleReportDateToDateChange = (date: Date | null) =>
    handleDateChange(date, setReportDateToDate);

  const workPackageOptions = formsListFilterOptions?.workPackages || [];

  const applyFiltersHandler = async () => {
    onFiltersUpdate(formFilters);
    await saveFormFiltersMutation({
      variables: {
        userId: me.id,
        data: JSON.stringify(formFilters),
      },
    });
    const existingPref = me.userPreferences?.find(
      p => p.entityType === "FormFilters"
    ) as UserPreferenceFormFilters | undefined;
    const updatedPref: UserPreferenceFormFilters = existingPref
      ? { ...existingPref, contents: formFilters }
      : {
          id: "local-form-pref",
          entityType: "FormFilters",
          contents: formFilters,
        };
    setUser({
      ...me,
      userPreferences: [
        ...(me.userPreferences?.filter(p => p.entityType !== "FormFilters") ??
          []),
        updatedPref,
      ],
    });
  };

  const clearFiltersHandler = () => {
    setApplyFiltersDisabled(false);
    setFormFilters(DEFAULT_FILTERS);
    setCreatedOnFromDate(null);
    setCreatedOnToDate(null);
    setUpdatedOnFromDate(null);
    setUpdatedOnToDate(null);
    setCompletedOnFromDate(null);
    setCompletedOnToDate(null);
    setReportDateFromDate(null);
    setReportDateToDate(null);
  };

  const getFilterField = (field: FilterField) => {
    const fieldValue = formFilters.find(
      filter => filter?.field === field
    ) as FormFilter;
    return fieldValue?.values;
  };

  const getFilterCount = (field: FilterField): number | undefined =>
    formFilters.find(filter => filter.field === field)?.values?.length;

  const filterUpdateHandler = (
    values: MultiOption[],
    field: FilterField
  ): void => {
    setApplyFiltersDisabled(false);
    setFormFilters(prevState => {
      const existingFilterIndex = prevState.findIndex(f => f.field === field);
      if (existingFilterIndex !== -1) {
        return prevState.map((f, index) =>
          index === existingFilterIndex ? { field, values } : f
        );
      }

      return [...prevState, { field, values }];
    });
  };

  const { data: createdByData } = useQuery(
    GET_FORMS_LIST_FILTER_OPTIONS_CREATED_BY_USERS,
    {
      variables: {
        limit: DEFAULT_LIMIT,
        offset,
        filterSearch: {
          searchColumn: "created_by_user",
          searchValue: searchQuery,
        },
      },
      onCompleted: newData => {
        const users = newData?.formsListFilterOptions?.createdByUsers || [];
        if (users.length === 0) setHasMore(false);
        else {
          setHasMore(true);
          setCreatedByUsers(prev => [...prev, ...users]);
        }
        if (createdByFlagRef.current) {
          createdByFlagRef.current = false;
          setOriginalCreatedByUsers(users);
        }
        setIsLoading(false);
      },
      onError: _err => {
        sessionExpiryHandlerForApolloClient(_err);
        toastCtx?.pushToast("error", "Error fetching form filters options");
      },
    }
  );

  const { data: updatedByData } = useQuery(
    GET_FORMS_LIST_FILTER_OPTIONS_UPDATED_BY_USERS,
    {
      variables: {
        limit: DEFAULT_LIMIT,
        offset: updatedByState.offset,
        filterSearch: {
          searchColumn: "updated_by_user",
          searchValue: updatedByState.searchQuery,
        },
      },
      onCompleted: newData => {
        const users = newData?.formsListFilterOptions?.updatedByUsers || [];
        if (users.length === 0) {
          dispatch({ type: "SET_HAS_MORE", payload: false });
        } else {
          dispatch({ type: "SET_HAS_MORE", payload: true });
          dispatch({ type: "APPEND_USERS", payload: users });
        }
        if (updatedByFlagRef.current) {
          updatedByFlagRef.current = false;
          dispatch({ type: "SET_ORIGINAL_USERS", payload: users });
        }
        dispatch({ type: "SET_LOADING", payload: false });
      },
      onError: _err => {
        sessionExpiryHandlerForApolloClient(_err);
        toastCtx?.pushToast("error", "Error fetching form filters options");
      },
    }
  );

  const handleScrollForUpdatedBy = (e: React.UIEvent<HTMLDivElement>) => {
    const container = e.target as HTMLDivElement;
    const isAtBottom =
      container.scrollHeight === container.scrollTop + container.clientHeight;

    if (isAtBottom && updatedByState.hasMore && !updatedByState.loading) {
      scrollPositionRefForUpdatedBy.current = container.scrollTop;
      dispatch({ type: "SET_LOADING", payload: true });
      dispatch({
        type: "SET_OFFSET",
        payload: updatedByState.offset + DEFAULT_LIMIT,
      });
    }
  };

  useEffect(() => {
    if (!updatedByState.loading && scrollContainerRefUpdatedBy.current) {
      scrollContainerRefUpdatedBy.current.scrollTop = scrollPositionRef.current;
    }
  }, [updatedByState.loading, updatedByState.users]);

  useEffect(() => {
    dispatch({ type: "SET_LOADING", payload: false });
  }, [updatedByData]);

  const handleUpdatedBySearchChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    dispatch({ type: "SET_LOCAL_VALUE", payload: e.target.value });
    debouncedUpdatedBySearch(e.target.value);
  };

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const container = e.target as HTMLDivElement;
    const isAtBottom =
      container.scrollHeight === container.scrollTop + container.clientHeight;

    if (isAtBottom && hasMore && !isLoading) {
      scrollPositionRef.current = container.scrollTop;
      setIsLoading(true);
      setOffset(prevOffset => prevOffset + DEFAULT_LIMIT);
    }
  };

  useEffect(() => {
    if (!isLoading && scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollPositionRef.current;
    }
  }, [isLoading, createdByUsers]);

  useEffect(() => {
    setIsLoading(false);
  }, [createdByData]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalValue(e.target.value);
    debouncedUpdateSearch(e.target.value);
  };

  const setCreatedTimeRange = useCallback(
    (from?: Date | null, to?: Date | null) => {
      if (from && to) {
        const timeRange = [
          { id: "startDate", name: from?.toISOString() ?? null },
          { id: "endDate", name: to?.toISOString() ?? null },
        ];
        filterUpdateHandler(timeRange, "CREATEDON");
      }
    },
    []
  );

  const setUpdatedTimeRange = useCallback(
    (from?: Date | null, to?: Date | null) => {
      if (from && to) {
        const timeRange = [
          { id: "startUpdatedAt", name: from?.toISOString() ?? null },
          { id: "endUpdatedAt", name: to?.toISOString() ?? null },
        ];
        filterUpdateHandler(timeRange, "UPDATEDON");
      }
    },
    []
  );

  const setCompletedTimeRange = useCallback(
    (from?: Date | null, to?: Date | null) => {
      if (from && to) {
        const timeRange = [
          { id: "startCompletedAt", name: from?.toISOString() ?? null },
          { id: "endCompletedAt", name: to?.toISOString() ?? null },
        ];
        filterUpdateHandler(timeRange, "COMPLETEDON");
      }
    },
    []
  );

  const setReportedTimeRange = useCallback(
    (from?: Date | null, to?: Date | null) => {
      if (from && to) {
        const timeRange = [
          { id: "startReportDate", name: from?.toISOString() ?? null },
          { id: "endReportDate", name: to?.toISOString() ?? null },
        ];
        filterUpdateHandler(timeRange, "REPORTDATE");
      }
    },
    []
  );

  useEffect(() => {
    const tenant = getTenantName();
    setTenantName(tenant);
  }, []);

  const getStatusLevels = () => {
    const baseStatusLevels = [StatusLevel.COMPLETE, StatusLevel.IN_PROGRESS];

    if (formStatusForNg.includes(tenantName)) {
      baseStatusLevels.push(StatusLevel.PENDING_POST_JOB_BRIEF);
      baseStatusLevels.push(StatusLevel.PENDING_SIGN_OFF);
    }
    return baseStatusLevels;
  };

  const statusLevels = getStatusLevels();
  const getStatusLevelOptions = statusLevels.map(status => ({
    id: status,
    name: status,
  }));

  useEffect(() => {
    const storedFilters = getFormFilters() ?? DEFAULT_FILTERS;
    setFormFilters(storedFilters);
  }, []);

  useEffect(() => {
    let to = null;
    let from = null;

    if (!createdOnFromDate && createdOnToDate) {
      from = getFilterField("CREATEDON")[0]?.name
        ? new Date(getFilterField("CREATEDON")[0]?.name)
        : null;
      to = createdOnToDate;
    } else if (createdOnFromDate && !createdOnToDate) {
      from = createdOnFromDate;
      to = new Date();
    } else if (createdOnFromDate && createdOnToDate) {
      from = createdOnFromDate;
      to = createdOnToDate;
    }

    setCreatedTimeRange(from, to);
  }, [createdOnToDate, createdOnFromDate]);

  useEffect(() => {
    let from = null;
    let to = null;
    if (!updatedOnFromDate && updatedOnToDate) {
      from = getFilterField("UPDATEDON")[0]?.name
        ? new Date(getFilterField("UPDATEDON")[0]?.name)
        : null;
      to = updatedOnToDate;
    } else if (updatedOnFromDate && !updatedOnToDate) {
      from = updatedOnFromDate;
      to = new Date();
    } else if (updatedOnFromDate && updatedOnToDate) {
      from = updatedOnFromDate;
      to = updatedOnToDate;
    }

    setUpdatedTimeRange(from, to);
  }, [updatedOnToDate, updatedOnFromDate]);

  useEffect(() => {
    let from = null,
      to = null;
    if (!completedOnFromDate && completedOnToDate) {
      from = getFilterField("COMPLETEDON")[0]?.name
        ? new Date(getFilterField("COMPLETEDON")[0]?.name)
        : null;
      to = completedOnToDate;
    } else if (completedOnFromDate && !completedOnToDate) {
      from = completedOnFromDate;
      to = new Date();
    } else if (completedOnFromDate && completedOnToDate) {
      from = completedOnFromDate;
      to = completedOnToDate;
    }

    setCompletedTimeRange(from, to);
  }, [completedOnToDate, completedOnFromDate]);

  useEffect(() => {
    let from = null;
    let to = null;
    if (!reportDateFromDate && reportDateToDate) {
      from = getFilterField("REPORTDATE")[0]?.name
        ? new Date(getFilterField("REPORTDATE")[0]?.name)
        : null;
      to = reportDateToDate;
    } else if (reportDateFromDate && !reportDateToDate) {
      from = reportDateFromDate;
      to = new Date();
    } else if (reportDateFromDate && reportDateToDate) {
      from = reportDateFromDate;
      to = reportDateToDate;
    }

    setReportedTimeRange(from, to);
  }, [reportDateFromDate, reportDateToDate]);

  const FiltersFooter = (
    <div className="flex justify-end gap-4 px-6 py-6">
      <ButtonTertiary label="Cancel" onClick={onClose} />
      <ButtonPrimary
        label="Apply"
        onClick={applyFiltersHandler}
        disabled={applyFiltersDisabled}
      />
    </div>
  );

  function removeUserFilter(userId: string, userType: string) {
    if (userType === "CREATEDBY") {
      const currentSelection = getFilterField("CREATEDBY") || [];
      const updated = currentSelection.filter(item => item.id !== userId);
      filterUpdateHandler(updated, "CREATEDBY");
    }
    if (userType === "UPDATEDBY") {
      const currentSelection = getFilterField("UPDATEDBY") || [];
      const updated = currentSelection.filter(item => item.id !== userId);
      filterUpdateHandler(updated, "UPDATEDBY");
    }
  }

  function handleSelectUser(user: MultiOption, userType: string) {
    if (userType === "CREATEDBY") {
      const currentSelection = getFilterField("CREATEDBY") || [];
      if (!currentSelection.some(item => item.id === user.id)) {
        filterUpdateHandler([...currentSelection, user], "CREATEDBY");
      }
      setLocalValue("");
      setSearchQuery("");
      setCreatedByUsers([...originalCreatedByUsers]);
    }
    if (userType === "UPDATEDBY") {
      const currentSelection = getFilterField("UPDATEDBY") || [];
      if (!currentSelection.some(item => item.id === user.id)) {
        filterUpdateHandler([...currentSelection, user], "UPDATEDBY");
      }
      dispatch({ type: "SET_LOCAL_VALUE", payload: "" });
      dispatch({ type: "SET_SEARCH_QUERY", payload: "" });
      dispatch({ type: "SET_USERS", payload: updatedByState.originalUsers });
    }
  }

  const workpackages = getFilterField("WORKPACKAGE");
  const adhocWorkpackageSelected = !!workpackages.find(
    wp => wp.name === "AD_HOC"
  );
  const filteredWorkpackages = workpackages.filter(wp => wp.name !== "AD_HOC");

  return (
    <Flyover
      isOpen={isOpen}
      title="Form Filters"
      unmount
      onClose={onClose}
      footer={FiltersFooter}
      footerStyle={"!relative right-0 !bottom-[1.5rem]"}
      className={"md:!w-[25rem]"}
    >
      <button
        className="font-semibold px-3 mb-3 text-brand-urbint-50 active:text-brand-urbint-60 hover:text-brand-urbint-40"
        onClick={clearFiltersHandler}
      >
        Clear all
      </button>

      {formList.attributes.formName.visible && (
        <FilterSection
          title={formList.attributes.formName.label}
          count={getFilterCount("FORM")}
        >
          <MultiOptionWrapper
            options={formIdOptions}
            value={getFilterField("FORM")}
            onSelect={options => filterUpdateHandler(options, "FORM")}
          />
        </FilterSection>
      )}
      {formList.attributes.formId.visible && (
        <FilterSection
          title={formList.attributes.formId.label}
          count={getFilterCount("FORMID")}
        >
          <MultiSelect
            options={idOptions}
            value={getFilterField("FORMID")}
            icon={"search"}
            placeholder={"Search for Forms with ID"}
            onSelect={options => {
              filterUpdateHandler(options as MultiOption[], "FORMID");
            }}
            isSearchable
          />
        </FilterSection>
      )}
      {formList.attributes.location.visible && (
        <FilterSection
          title={formList.attributes.location.label}
          count={getFilterCount("LOCATIONS")}
        >
          {loading ? (
            <LoadingFiltersComponent icon="search" />
          ) : (
            <MultiSelect
              options={locationsOption}
              value={getFilterField("LOCATIONS")}
              icon={"search"}
              placeholder={"Search for location"}
              onSelect={options =>
                filterUpdateHandler(options as MultiOption[], "LOCATIONS")
              }
              isSearchable
            />
          )}
        </FilterSection>
      )}
      {formList.attributes.status.visible && (
        <FilterSection
          title={formList.attributes.status.label}
          count={getFilterCount("STATUS")}
        >
          <MultiOptionWrapper
            options={getStatusLevelOptions}
            value={getFilterField("STATUS")}
            onSelect={options => filterUpdateHandler(options, "STATUS")}
          />
        </FilterSection>
      )}
      {formList.attributes.operatingHQ.visible && (
        <FilterSection
          count={getFilterCount("OPERATINGHQ")}
          title={formList.attributes.operatingHQ.label}
        >
          {loading ? (
            <LoadingFiltersComponent icon="search" />
          ) : (
            <MultiSelect
              isSearchable
              icon="search"
              options={operatingHqOptions}
              value={getFilterField("OPERATINGHQ")}
              onSelect={options =>
                filterUpdateHandler(options as MultiOption[], "OPERATINGHQ")
              }
              placeholder={`Search for ${formList.attributes.operatingHQ.labelPlural}`}
            />
          )}
        </FilterSection>
      )}
      {formList.attributes.workPackage.visible && (
        <FilterSection
          title={formList.attributes.workPackage.label}
          count={getFilterCount("WORKPACKAGE")}
        >
          <div className="flex justify-between mb-4">
            <label>Show Ad-hoc only</label>
            <Toggle
              checked={adhocWorkpackageSelected}
              onClick={() => {
                if (adhocWorkpackageSelected) {
                  filterUpdateHandler([], "WORKPACKAGE");
                } else {
                  filterUpdateHandler(
                    [{ id: "", name: "AD_HOC" }],
                    "WORKPACKAGE"
                  );
                }
              }}
            />
          </div>
          {!adhocWorkpackageSelected && (
            <MultiSelect
              options={workPackageOptions}
              value={filteredWorkpackages}
              icon={"search"}
              placeholder={`Search for ${formList.attributes.workPackage.labelPlural}`}
              onSelect={options => {
                filterUpdateHandler(options as MultiOption[], "WORKPACKAGE");
              }}
              isSearchable
            />
          )}
        </FilterSection>
      )}
      {formList.attributes.createdBy.visible && (
        <FilterSection
          title={formList.attributes.createdBy.label}
          count={getFilterCount("CREATEDBY")}
        >
          {loading ? (
            <LoadingFiltersComponent icon="search" />
          ) : (
            <>
              <InputWithChips
                value={localValue}
                placeholder="Search for users"
                icon="search"
                chips={getFilterField("CREATEDBY") || []}
                onRemoveChip={(chipId: string) =>
                  removeUserFilter(chipId, "CREATEDBY")
                }
                onChange={handleSearchChange}
                className="text-[1.060rem]"
              />
              <div
                className="bg-white border border-gray-300 rounded-md shadow-lg mt-2 overflow-y-auto max-h-[15rem]"
                onScroll={handleScroll}
                ref={scrollContainerRef}
              >
                <ul>
                  {createdByUsers.length > 0 ? (
                    createdByUsers.map(user => (
                      <li
                        key={user.id}
                        className="cursor-pointer hover:bg-gray-200 p-2"
                        onClick={() => handleSelectUser(user, "CREATEDBY")}
                      >
                        {user.name}
                      </li>
                    ))
                  ) : hasMore === false ? (
                    <BodyText className="p-2">No Options Available</BodyText>
                  ) : (
                    <div className="p-2">
                      <CircularLoader />
                    </div>
                  )}
                </ul>

                {isLoading && (
                  <BodyText className="text-center p-2">
                    Loading more...
                  </BodyText>
                )}
              </div>
            </>
          )}
        </FilterSection>
      )}
      {formList.attributes.createdOn.visible && (
        <FilterSection
          title={formList.attributes.createdOn.label}
          count={getFilterCount("CREATEDON") == 2 ? 1 : 0}
        >
          <div className="flex flex-row text-base font-semibold text-neutral-shade-75 justify-between">
            <div className="w-[10.5rem]">
              <label>From</label>
              <InputDateSelect
                icon="calendar"
                placeholder="Select a date"
                selectedDate={
                  getFilterField("CREATEDON")[0]
                    ? new Date(getFilterField("CREATEDON")[0].name)
                    : null
                }
                onDateChange={handleCreatedOnFormDateChange}
                maxDate={new Date()}
                dateFormat={"MM-dd-yyyy"}
              />
            </div>
            <div className="w-[10.5rem]">
              <label>To</label>
              <InputDateSelect
                icon="calendar"
                placeholder="Select a date"
                selectedDate={
                  getFilterField("CREATEDON")[1]
                    ? new Date(getFilterField("CREATEDON")[1].name)
                    : null
                }
                onDateChange={handleCreatedOnToDateChange}
                minDate={createdOnFromDate}
                maxDate={new Date()}
                dateFormat={"MM-dd-yyyy"}
                disabled={
                  !(
                    getFilterField("CREATEDON") &&
                    getFilterField("CREATEDON")[0]
                  )
                }
              />
            </div>
          </div>
        </FilterSection>
      )}
      {formList.attributes.updatedBy.visible && (
        <FilterSection
          title={formList.attributes.updatedBy?.label}
          count={getFilterCount("UPDATEDBY")}
        >
          {loading ? (
            <LoadingFiltersComponent icon="search" />
          ) : (
            <>
              <InputWithChips
                value={updatedByState.localValue}
                placeholder="Search for users"
                icon="search"
                chips={getFilterField("UPDATEDBY") || []}
                onRemoveChip={(chipId: string) =>
                  removeUserFilter(chipId, "UPDATEDBY")
                }
                onChange={handleUpdatedBySearchChange}
                className="text-[1.060rem]"
              />
              <div
                className="bg-white border border-gray-300 rounded-md shadow-lg mt-2 overflow-y-auto max-h-[15rem]"
                onScroll={handleScrollForUpdatedBy}
                ref={scrollContainerRefUpdatedBy}
              >
                <ul>
                  {updatedByState.users.length > 0 ? (
                    updatedByState.users.map(user => (
                      <li
                        key={user.id}
                        className="cursor-pointer hover:bg-gray-200 p-2"
                        onClick={() => handleSelectUser(user, "UPDATEDBY")}
                      >
                        {user.name}
                      </li>
                    ))
                  ) : updatedByState.hasMore === false ? (
                    <BodyText className="p-2">No Options Available</BodyText>
                  ) : (
                    <div className="p-2">
                      <CircularLoader />
                    </div>
                  )}
                </ul>
                {updatedByState.loading && (
                  <BodyText className="text-center p-2">
                    Loading More ...
                  </BodyText>
                )}
              </div>
            </>
          )}
        </FilterSection>
      )}
      {formList.attributes.updatedOn.visible && (
        <FilterSection
          title={formList.attributes.updatedOn?.label}
          count={getFilterCount("UPDATEDON") == 2 ? 1 : 0}
        >
          <div className="flex flex-row text-base font-semibold text-neutral-shade-75 justify-between">
            <div className="w-[10.5rem]">
              <label>From</label>
              <InputDateSelect
                icon="calendar"
                placeholder="Select a date"
                selectedDate={
                  getFilterField("UPDATEDON")[0]
                    ? new Date(getFilterField("UPDATEDON")[0].name)
                    : null
                }
                onDateChange={handleUpdatedOnFromDateChange}
                maxDate={new Date()}
                dateFormat={"MM-dd-yyyy"}
              />
            </div>
            <div className="w-[10.5rem]">
              <label>To</label>
              <InputDateSelect
                icon="calendar"
                placeholder="Select a date"
                selectedDate={
                  getFilterField("UPDATEDON")[1]
                    ? new Date(getFilterField("UPDATEDON")[1].name)
                    : null
                }
                onDateChange={handleUpdatedToDateChange}
                minDate={updatedOnFromDate} // Set minDate to From Date
                maxDate={new Date()}
                dateFormat={"MM-dd-yyyy"}
                disabled={
                  !(
                    getFilterField("UPDATEDON") &&
                    getFilterField("UPDATEDON")[0]
                  )
                }
              />
            </div>
          </div>
        </FilterSection>
      )}
      {formList.attributes.completedOn.visible && (
        <FilterSection
          title={formList.attributes.completedOn?.label}
          count={getFilterCount("COMPLETEDON") === 2 ? 1 : 0}
        >
          <div className="flex flex-row text-base font-semibold text-neutral-shade-75 justify-between">
            <div className="w-[10.5rem]">
              <label>From</label>
              <InputDateSelect
                icon="calendar"
                placeholder="Select a date"
                selectedDate={
                  getFilterField("COMPLETEDON")[0]
                    ? new Date(getFilterField("COMPLETEDON")[0].name)
                    : null
                }
                onDateChange={handleCompletedOnFromDateChange}
                maxDate={new Date()}
                dateFormat={"MM-dd-yyyy"}
              />
            </div>
            <div className="w-[10.5rem]">
              <label>To</label>
              <InputDateSelect
                icon="calendar"
                placeholder="Select a date"
                selectedDate={
                  getFilterField("COMPLETEDON")[1]
                    ? new Date(getFilterField("COMPLETEDON")[1].name)
                    : null
                }
                onDateChange={handleCompletedOnToDateChange}
                minDate={completedOnFromDate} // Set minDate to From Date
                maxDate={new Date()}
                dateFormat={"MM-dd-yyyy"}
                disabled={
                  !(
                    getFilterField("COMPLETEDON") &&
                    getFilterField("COMPLETEDON")[0]
                  )
                }
              />
            </div>
          </div>
        </FilterSection>
      )}
      {formList.attributes.date.visible && (
        <FilterSection
          title={formList.attributes.date.label}
          count={getFilterCount("REPORTDATE") === 2 ? 1 : 0}
        >
          <div className="flex flex-row text-base font-semibold text-neutral-shade-75 justify-between">
            <div className="w-[10.5rem]">
              <label>From</label>
              <InputDateSelect
                icon="calendar"
                placeholder="Select a date"
                selectedDate={
                  getFilterField("REPORTDATE")[0]
                    ? new Date(getFilterField("REPORTDATE")[0].name)
                    : null
                }
                onDateChange={handleReportDateFromDateChange}
                maxDate={new Date()}
                dateFormat={"MM-dd-yyyy"}
              />
            </div>
            <div className="w-[10.5rem]">
              <label>To</label>
              <InputDateSelect
                icon="calendar"
                placeholder="Select a date"
                selectedDate={
                  getFilterField("REPORTDATE")[1]
                    ? new Date(getFilterField("REPORTDATE")[1].name)
                    : null
                }
                onDateChange={handleReportDateToDateChange}
                minDate={reportDateFromDate} // Set minDate to From Date
                maxDate={new Date()}
                dateFormat={"MM-dd-yyyy"}
                disabled={
                  !(
                    getFilterField("REPORTDATE") &&
                    getFilterField("REPORTDATE")[0]
                  )
                }
              />
            </div>
          </div>
        </FilterSection>
      )}
      {formList.attributes.supervisor.visible && (
        <FilterSection
          count={getFilterCount("SUPERVISOR")}
          title={formList.attributes.supervisor.label}
        >
          {loading ? (
            <LoadingFiltersComponent icon="search" />
          ) : (
            <MultiSelect
              icon={"search"}
              options={supervisorOption}
              value={getFilterField("SUPERVISOR")}
              placeholder={"Search for supervisor"}
              onSelect={options =>
                filterUpdateHandler(options as MultiOption[], "SUPERVISOR")
              }
              isSearchable
            />
          )}
        </FilterSection>
      )}
    </Flyover>
  );
}
