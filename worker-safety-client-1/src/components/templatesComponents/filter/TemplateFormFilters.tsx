import axiosRest from "@/api/customFlowApi";
import { UserPreferenceEntityType } from "@/api/generated/types";
import Flyover from "@/components/flyover/Flyover";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ButtonTertiary from "@/components/shared/button/tertiary/ButtonTertiary";
import InputDateSelect from "@/components/shared/inputDateSelect/InputDateSelect";
import MultiSelect from "@/components/shared/inputSelect/multiSelect/MultiSelect";
import { StatusLevel } from "@/components/statusBadge/StatusLevel";
import { config } from "@/config";
import useRestMutation from "@/hooks/useRestMutation";
import SaveTemplateFormFiltersMutation from "@/pages/forms/SaveTemplateFormFilters.mutation.gql";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import type { UserPreferenceCWFTemplateFormFilters } from "@/types/auth/AuthUser";
import { useMutation } from "@apollo/client";
import { isArray } from "lodash-es";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useTemplateFormsFilterContext } from "../context/TemplateFormsFiltersProvider";
import type {
  MultiOption,
  TemplatesFormListFilter,
} from "../customisedForm.types";
import {
  removeDuplicatesById,
  removeDuplicatesByName,
} from "../customisedForm.utils";
import FilterSection from "../filterSection/FilterSection";
import MultiOptionWrapper from "../multiOptionWrapper/MultiOptionWrapper";

export type TemplateFormFiltersProps = {
  isOpen: boolean;
  onClose: () => void;
  onFiltersApply: (filters: TemplateFormsFilter[]) => void;
};

type FilterField =
  | "FORMNAME"
  | "STATUS"
  | "CREATEDBY"
  | "CREATEDON"
  | "UPDATEDBY"
  | "UPDATEDON"
  | "COMPLETEDON"
  | "REPORTEDON"
  | "WORKPACKAGE"
  | "LOCATION"
  | "REGION"
  | "SUPERVISOR";

export type TemplateFormsFilter = {
  field: FilterField;
  values: MultiOption[];
};

const statusLevels = [StatusLevel.COMPLETE, StatusLevel.IN_PROGRESS];

const getStatusLevelOptions = statusLevels.map(status => ({
  id: status == "In-Progress" ? "in_progress" : status.toLowerCase(),
  name: status,
}));

export default function TemplateFormFilters({
  isOpen,
  onClose,
  onFiltersApply,
}: TemplateFormFiltersProps): JSX.Element {
  const { me, setUser } = useAuthStore();
  const [saveTemplateFormFiltersMutation] = useMutation(
    SaveTemplateFormFiltersMutation
  );
  const { templateForm } = useTenantStore(state => state.getAllEntities());
  const { filters: activeFilters, setFilters } =
    useTemplateFormsFilterContext();
  function isCWFFPref(p: any): p is UserPreferenceCWFTemplateFormFilters {
    return p.entityType === "CWFTemplateFormFilters";
  }
  const savedPref = me.userPreferences?.find(isCWFFPref);
  const storedValue: TemplateFormsFilter[] =
    savedPref?.contents ?? activeFilters;
  const [applyFilterActive, setApplyFilterActive] = useState<boolean>(true);

  const [formFilters, setFormFilters] =
    useState<TemplateFormsFilter[]>(storedValue);
  const [fromDate, setFromDate] = useState<Date | null>(null);
  const [toDate, setToDate] = useState<Date | null>(null);
  const [updatedOnFromDate, setUpdatedOnFromDate] = useState<Date | null>(null);
  const [updatedOnToDate, setUpdatedOnToDate] = useState<Date | null>(null);
  const [completedOnFromDate, setCompletedOnFromDate] = useState<Date | null>(
    null
  );
  const [completedOnToDate, setCompletedOnToDate] = useState<Date | null>(null);
  const [reportedOnFromDate, setReportedOnFromDate] = useState<Date | null>(
    null
  );
  const [reportedOnToDate, setReportedOnToDate] = useState<Date | null>(null);

  const handleFromDateChange = (date: Date | null) => {
    setFromDate(date);
    if (date === null) {
      filterUpdateHandler([], "CREATEDON");
    }
  };

  const handleToDateChange = (date: Date | null) => {
    setToDate(date);
  };
  const handleUpdatedOnFromDateChange = (date: Date | null) => {
    setUpdatedOnFromDate(date);
    if (date === null) {
      filterUpdateHandler([], "UPDATEDON");
    }
  };

  const handleReportedOnFromDateChange: (date: Date | null) => void = date => {
    setReportedOnFromDate(date);
    if (date === null) {
      setReportedOnToDate(null);
      filterUpdateHandler([], "REPORTEDON");
    }
  };

  const handleReportedOnToDateChange: (date: Date | null) => void = date => {
    setReportedOnToDate(date);
  };

  const handleUpdatedToDateChange = (date: Date | null) => {
    setUpdatedOnToDate(date);
  };

  const handleCompletedOnFromDateChange = (date: Date | null) => {
    setCompletedOnFromDate(date);
    if (date === null) {
      filterUpdateHandler([], "COMPLETEDON");
    }
  };

  const handleCompletedToDateChange = (date: Date | null) => {
    setCompletedOnToDate(date);
  };

  const [formsListData, setFormsListData] = useState<TemplatesFormListFilter>();

  const { mutate: fetchFormsList } = useRestMutation<any>({
    endpoint: `${config.workerSafetyCustomWorkFlowUrlRest}/forms/list/filter-options`,
    method: "get",
    axiosInstance: axiosRest,
    dtoFn: data => data,
    mutationOptions: {
      onSuccess: (responseData: any) => {
        if (responseData.data) {
          setFormsListData(responseData.data);
        }
      },
      onError: () => {
        console.log("Failed to Load Forms Data");
      },
    },
  });

  const formNamesFromResponse = useMemo(() => {
    if (!formsListData || !isArray(formsListData.names)) {
      return [];
    }
    return removeDuplicatesByName(
      formsListData?.names.map((item: string, index: number) => ({
        id: `${index}`,
        name: item,
      }))
    );
  }, [formsListData]);

  const workPackagesFromResponse = useMemo(() => {
    if (!formsListData || !isArray(formsListData.work_package)) {
      return [];
    }

    return removeDuplicatesById(
      formsListData.work_package.map((item: MultiOption) => ({
        id: item.id,
        name: item.name,
      }))
    );
  }, [formsListData]);

  const workPackagesRegionFromResponse = useMemo(() => {
    if (!formsListData || !isArray(formsListData.region)) {
      return [];
    }

    return removeDuplicatesByName(
      formsListData.region.map((item: MultiOption) => ({
        id: item.id,
        name: item.name,
      }))
    );
  }, [formsListData]);

  const workPackagesLocationFromResponse = useMemo(() => {
    if (!formsListData || !isArray(formsListData.location)) {
      return [];
    }
    return removeDuplicatesById(
      formsListData.location.map((item: MultiOption) => ({
        id: item.id,
        name: item.name,
      }))
    );
  }, [formsListData]);

  const createdByOptions = useMemo(() => {
    if (!formsListData || !isArray(formsListData.created_by_users)) {
      return [];
    }
    return removeDuplicatesByName(
      formsListData.created_by_users.map((item: MultiOption) => ({
        id: item.id,
        name: item.name,
      }))
    );
  }, [formsListData]);

  const updatedByOptions = useMemo(() => {
    if (!formsListData || !isArray(formsListData.updated_by_users)) {
      return [];
    }
    return removeDuplicatesByName(
      formsListData.updated_by_users.map((item: MultiOption) => ({
        id: item.id,
        name: item.name,
      }))
    );
  }, [formsListData]);

  const supervisorList = useMemo(() => {
    if (!formsListData || !isArray(formsListData.supervisor)) {
      return [];
    }
    return removeDuplicatesByName(
      formsListData.supervisor.map((item: MultiOption) => ({
        id: item.id,
        name: item.name,
      }))
    );
  }, [formsListData]);

  useEffect(() => {
    setFormFilters(storedValue);
    if (isOpen === true) {
      fetchFormsList({ offset: 0 });
    }

    try {
      const isFilterApplied = storedValue.reduce(
        (acc, filter) => acc + filter.values.length,
        0
      );
      if (isFilterApplied === 0) {
        setApplyFilterActive(true);
      }
    } catch (err) {
      setApplyFilterActive(false);
      console.log(err);
    }
  }, [isOpen]);

  function isCWFPref(p: any): p is UserPreferenceCWFTemplateFormFilters {
    return p.entityType === "CWFTemplateFormFilters";
  }
  const existingPref = me.userPreferences?.find(isCWFPref);

  const applyFiltersHandler = async () => {
    await saveTemplateFormFiltersMutation({
      variables: {
        userId: me.id,
        entityType: UserPreferenceEntityType.CwfTemplateFormFilters,
        data: JSON.stringify(formFilters),
      },
    });

    const updatedPref: UserPreferenceCWFTemplateFormFilters = existingPref
      ? { ...existingPref, contents: formFilters }
      : {
          id: "local-form-cwf-form-pref",
          entityType: "CWFTemplateFormFilters",
          contents: formFilters,
        };

    setUser({
      ...me,
      userPreferences: [
        ...(me.userPreferences?.filter(
          p => p.entityType !== "CWFTemplateFormFilters"
        ) ?? []),
        updatedPref,
      ],
    });
    onFiltersApply(formFilters);
    setFilters(formFilters);
  };

  const clearFiltersHandler = () => {
    setFormFilters(activeFilters);
    setFromDate(null);
    setToDate(null);
    setUpdatedOnFromDate(null);
    setUpdatedOnToDate(null);
  };

  const getFilterField = (field: FilterField) => {
    const fieldValue = formFilters.find(
      filter => filter?.field === field
    ) as TemplateFormsFilter;
    return fieldValue?.values;
  };

  const getFilterCount = (field: FilterField): number | undefined =>
    formFilters.find(filter => filter.field === field)?.values?.length;

  const totalFilterSelected = formFilters.reduce(
    (acc, filter) => acc + filter.values.length,
    0
  );
  useEffect(() => {
    if (totalFilterSelected > 0) {
      setApplyFilterActive(false);
    }
  }, [totalFilterSelected]);

  const filterUpdateHandler = (
    values: MultiOption[],
    field: FilterField
  ): void => {
    setFormFilters(prevState =>
      prevState.map(filter =>
        filter.field === field ? { field, values } : filter
      )
    );
  };

  const filtersFooter = (
    <div className="flex justify-end gap-4 px-6 py-6">
      <ButtonTertiary label="Cancel" onClick={onClose} />
      <ButtonPrimary
        label="Apply"
        onClick={applyFiltersHandler}
        disabled={applyFilterActive}
      />
    </div>
  );

  // Helper function to create date range with start/end of day
  const createDateRange = useCallback((from, to, startId, endId) => {
    if (!from || !to) return null;

    // Create start of day in local timezone, then convert to UTC
    const startDate = new Date(from);
    startDate.setHours(0, 0, 0, 0);

    // Create end of day in local timezone, then convert to UTC
    const endDate = new Date(to);
    endDate.setHours(23, 59, 59, 999);

    return [
      { id: startId, name: startDate?.toISOString() ?? null },
      { id: endId, name: endDate?.toISOString() ?? null },
    ];
  }, []);

  const setCreatedTimeRange = useCallback(
    function (from, to) {
      const timeRange = createDateRange(from, to, "startDate", "endDate");
      if (timeRange) {
        filterUpdateHandler(timeRange, "CREATEDON");
      }
    },
    [createDateRange]
  );

  const setUpdatedTimeRange = useCallback(
    function (from, to) {
      const timeRange = createDateRange(
        from,
        to,
        "startUpdatedAt",
        "endUpdatedAt"
      );
      if (timeRange) {
        filterUpdateHandler(timeRange, "UPDATEDON");
      }
    },
    [createDateRange]
  );

  const setCompletedTimeRange = useCallback(
    function (from, to) {
      const timeRange = createDateRange(
        from,
        to,
        "startCompletedAt",
        "endCompletedAt"
      );
      if (timeRange) {
        filterUpdateHandler(timeRange, "COMPLETEDON");
      }
    },
    [createDateRange]
  );

  const setReportedTimeRange = useCallback(
    function (from, to) {
      const timeRange = createDateRange(
        from,
        to,
        "reported_at_start_date",
        "reported_at_end_date"
      );
      if (timeRange) {
        filterUpdateHandler(timeRange, "REPORTEDON");
      }
    },
    [createDateRange]
  );

  useEffect(() => {
    try {
      const createdOnFilter = getFilterField("CREATEDON") || [];
      const updatedOnFilter = getFilterField("UPDATEDON") || [];
      const completedOnFilter = getFilterField("COMPLETEDON") || [];
      const reportedOnFilter = getFilterField("REPORTEDON") || [];

      if (createdOnFilter.length > 0 && createdOnFilter[0]?.name) {
        setFromDate(new Date(createdOnFilter[0]?.name));
        setToDate(new Date(createdOnFilter[1]?.name));
      }

      if (updatedOnFilter.length > 0 && updatedOnFilter[0]?.name) {
        setUpdatedOnFromDate(new Date(updatedOnFilter[0]?.name));
        setUpdatedOnToDate(new Date(updatedOnFilter[1]?.name));
      }

      if (completedOnFilter.length > 0 && completedOnFilter[0]?.name) {
        setCompletedOnFromDate(new Date(completedOnFilter[0]?.name));
        setCompletedOnToDate(new Date(completedOnFilter[1]?.name));
      }
      if (reportedOnFilter.length > 0 && reportedOnFilter[0]?.name) {
        setReportedOnFromDate(new Date(reportedOnFilter[0]?.name));
        setReportedOnToDate(new Date(reportedOnFilter[1]?.name));
      }
    } catch {
      setFormFilters(activeFilters);
    }
  }, []);

  useEffect(() => {
    let from = null;
    let to = null;

    if (!fromDate && toDate) {
      from = getFilterField("CREATEDON")[0]?.name
        ? new Date(getFilterField("CREATEDON")[0]?.name)
        : null;
      to = toDate;
    } else if (fromDate && !toDate) {
      from = fromDate;
      to = new Date();
    } else if (fromDate && toDate) {
      from = fromDate;
      to = toDate;
    }

    setCreatedTimeRange(from, to);
  }, [toDate, fromDate]);

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
    let from = null;
    let to = null;
    if (!reportedOnFromDate && reportedOnToDate) {
      from = getFilterField("REPORTEDON")[0]?.name
        ? new Date(getFilterField("REPORTEDON")[0]?.name)
        : null;
      to = reportedOnToDate;
    } else if (reportedOnFromDate && !reportedOnToDate) {
      from = reportedOnFromDate;
      to = new Date();
    } else if (reportedOnFromDate && reportedOnToDate) {
      from = reportedOnFromDate;
      to = reportedOnToDate;
    }
    setReportedTimeRange(from, to);
  }, [reportedOnToDate, reportedOnFromDate]);

  useEffect(() => {
    let from = null;
    let to = null;
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

  return (
    <Flyover
      isOpen={isOpen}
      title={`${templateForm?.labelPlural} Filters`}
      unmount
      onClose={onClose}
      footer={filtersFooter}
      footerStyle={"!relative right-0 !bottom-[1.5rem]"}
      className={"md:!w-[25rem]"}
    >
      <button
        className="font-semibold px-3 mb-3 text-brand-urbint-50 active:text-brand-urbint-60 hover:text-brand-urbint-40"
        onClick={clearFiltersHandler}
      >
        Clear all
      </button>
      {templateForm.attributes.formName?.visible && (
        <FilterSection
          title={templateForm.attributes.formName.label}
          count={getFilterCount("FORMNAME")}
        >
          <MultiSelect
            options={formNamesFromResponse}
            value={getFilterField("FORMNAME")}
            icon={"search"}
            placeholder={`Search for ${templateForm?.labelPlural}`}
            onSelect={options =>
              filterUpdateHandler(options as MultiOption[], "FORMNAME")
            }
            isSearchable
          />
        </FilterSection>
      )}
      {templateForm.attributes.status?.visible && (
        <FilterSection
          title={templateForm.attributes.status.label}
          count={getFilterCount("STATUS")}
        >
          <MultiOptionWrapper
            options={getStatusLevelOptions}
            value={getFilterField("STATUS")}
            onSelect={option => {
              filterUpdateHandler(option, "STATUS");
            }}
          />
        </FilterSection>
      )}
      {templateForm.attributes.createdBy?.visible && (
        <FilterSection
          title={templateForm.attributes.createdBy.label}
          count={getFilterCount("CREATEDBY")}
        >
          <MultiSelect
            options={createdByOptions}
            value={getFilterField("CREATEDBY")}
            icon={"search"}
            placeholder={"Search for users"}
            onSelect={options => {
              filterUpdateHandler(options as MultiOption[], "CREATEDBY");
            }}
            isSearchable
          />
        </FilterSection>
      )}

      {templateForm.attributes.createdOn?.visible && (
        <FilterSection
          title={templateForm.attributes.createdOn.label}
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
                onDateChange={handleFromDateChange}
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
                onDateChange={handleToDateChange}
                minDate={fromDate} // Set minDate to From Date
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
      {templateForm.attributes.updatedBy?.visible && (
        <FilterSection
          title={templateForm.attributes.updatedBy?.label}
          count={getFilterCount("UPDATEDBY")}
        >
          <MultiSelect
            options={updatedByOptions}
            value={getFilterField("UPDATEDBY")}
            icon={"search"}
            placeholder={"Search for users"}
            onSelect={options => {
              filterUpdateHandler(options as MultiOption[], "UPDATEDBY");
            }}
            isSearchable
          />
        </FilterSection>
      )}
      {templateForm.attributes.updatedOn?.visible && (
        <FilterSection
          title={templateForm.attributes.updatedOn?.label}
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

      {templateForm.attributes.completedOn?.visible && (
        <FilterSection
          title={templateForm.attributes.completedOn?.label}
          count={getFilterCount("COMPLETEDON") == 2 ? 1 : 0}
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
                onDateChange={handleCompletedToDateChange}
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

      {templateForm.attributes.reportDate?.visible && (
        <FilterSection
          title={templateForm.attributes.reportDate.label}
          count={getFilterCount("REPORTEDON") == 2 ? 1 : 0}
        >
          <div className="flex flex-row text-base font-semibold text-neutral-shade-75 justify-between">
            <div className="w-[10.5rem]">
              <label>From</label>
              <InputDateSelect
                icon="calendar"
                placeholder="Select a date"
                selectedDate={
                  getFilterField("REPORTEDON")[0]
                    ? new Date(getFilterField("REPORTEDON")[0].name)
                    : null
                }
                onDateChange={handleReportedOnFromDateChange}
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
                  getFilterField("REPORTEDON")[1]
                    ? new Date(getFilterField("REPORTEDON")[1].name)
                    : null
                }
                onDateChange={handleReportedOnToDateChange}
                minDate={reportedOnFromDate} // Set minDate to From Date
                maxDate={new Date()}
                dateFormat={"MM-dd-yyyy"}
                disabled={
                  !(
                    getFilterField("REPORTEDON") &&
                    getFilterField("REPORTEDON")[0]
                  )
                }
              />
            </div>
          </div>
        </FilterSection>
      )}
      {templateForm.attributes.Project?.visible && (
        <FilterSection
          title={templateForm.attributes.Project.label}
          count={getFilterCount("WORKPACKAGE")}
        >
          <MultiSelect
            options={workPackagesFromResponse}
            value={getFilterField("WORKPACKAGE")}
            icon={"search"}
            placeholder={"Search for Projects"}
            onSelect={options =>
              filterUpdateHandler(options as MultiOption[], "WORKPACKAGE")
            }
            isSearchable
          />
        </FilterSection>
      )}

      {templateForm.attributes.location?.visible && (
        <FilterSection
          title={templateForm.attributes.location.label}
          count={getFilterCount("LOCATION")}
        >
          <MultiSelect
            options={workPackagesLocationFromResponse}
            value={getFilterField("LOCATION")}
            icon={"search"}
            placeholder={"Search for Locations"}
            onSelect={options =>
              filterUpdateHandler(options as MultiOption[], "LOCATION")
            }
            isSearchable
          />
        </FilterSection>
      )}

      {templateForm.attributes.region?.visible && (
        <FilterSection
          title={templateForm.attributes.region.label}
          count={getFilterCount("REGION")}
        >
          <MultiSelect
            options={workPackagesRegionFromResponse}
            value={getFilterField("REGION")}
            icon={"search"}
            placeholder={"Search for Regions"}
            onSelect={options =>
              filterUpdateHandler(options as MultiOption[], "REGION")
            }
            isSearchable
          />
        </FilterSection>
      )}
      {templateForm.attributes.supervisor?.visible && (
        <FilterSection
          title={templateForm.attributes.supervisor?.label}
          count={getFilterCount("SUPERVISOR")}
        >
          <MultiSelect
            options={supervisorList}
            value={getFilterField("SUPERVISOR")}
            icon={"search"}
            placeholder={"Search for users"}
            onSelect={options => {
              filterUpdateHandler(options as MultiOption[], "SUPERVISOR");
            }}
            isSearchable
          />
        </FilterSection>
      )}
    </Flyover>
  );
}
