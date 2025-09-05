import type {
  DraftFilter,
  FilterField,
  PublishedFilter,
} from "@/types/Templates/TemplateLists";
import type {
  MultiOption,
  TemplatesListRequest,
} from "../customisedForm.types";
import React, { useEffect, useMemo, useState } from "react";
import { isArray } from "lodash-es";
import Flyover from "@/components/flyover/Flyover";
import FilterSection from "@/components/templatesComponents/filterSection/FilterSection";
import MultiSelect from "@/components/shared/inputSelect/multiSelect/MultiSelect";
import InputDateSelect from "@/components/shared/inputDateSelect/InputDateSelect";
import ButtonTertiary from "@/components/shared/button/tertiary/ButtonTertiary";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import { getDateFilterField, getFilterField } from "@/pages/templates";
import useRestMutation from "../../../hooks/useRestMutation";
import axiosRest from "../../../api/customFlowApi";
import { removeDuplicatesByName } from "../customisedForm.utils";

type MainFiltersProps = {
  data: any;
  isOpen: boolean;
  onClose: () => void;
  onApply: (filters: any) => void;
  filtersValues: Array<PublishedFilter | DraftFilter>;
  onClear: () => void;
  onChangeFilter: (filter: PublishedFilter | DraftFilter) => void;
  type: "published" | "draft";
};

type TemplatesListFilter = {
  names: MultiOption;
  published_by_users: string[];
};

const getFiltersCount = (
  filters: Array<PublishedFilter | DraftFilter>,
  type: FilterField
) => {
  if (!filters) return 0;
  const field = filters.find(filter => filter.field === type);
  if (field) {
    if (isArray(field.values)) {
      return field.values.length;
    }
    return field.values.from || field.values.to ? 1 : 0;
  }
  return 0;
};

const getUpdatedByFilterOptions = (data: any) => {
  return data?.updated_by_users?.map((item: MultiOption) => ({
    id: item?.id,
    name: item?.name,
  }));
};

const getPublishedByFilterOptions = (data: any) => {
  return data?.published_by_users.map((item: MultiOption) => ({
    id: item?.id,
    name: item?.name,
  }));
};

const MainFilters: React.FC<MainFiltersProps> = props => {
  const { isOpen, onClose, onApply, filtersValues, onChangeFilter, type } =
    props;

  const [templateData, setTemplateData] = useState<TemplatesListFilter>();
  // Local state to track working filters (what user is currently selecting)
  const [workingFilters, setWorkingFilters] =
    useState<Array<PublishedFilter | DraftFilter>>(filtersValues);
  // Track the applied filters (what was last applied)
  const [appliedFilters, setAppliedFilters] =
    useState<Array<PublishedFilter | DraftFilter>>(filtersValues);

  const { mutate: fetchTemplatesList } = useRestMutation<any>({
    endpoint: `/templates/list/filter-options?status=${type}`,
    method: "get",
    axiosInstance: axiosRest,
    dtoFn: data => data,
    mutationOptions: {
      onError: err => {
        console.log(err, "Error");
      },
      onSuccess: (data: any) => {
        setTemplateData(data.data);
      },
    },
  });

  // When the flyover opens, initialize working filters with current applied filters
  useEffect(() => {
    if (isOpen === true) {
      const requestData: TemplatesListRequest = { template_status: [type] };
      fetchTemplatesList(requestData);
      // Reset working filters to match the applied filters when opening
      setWorkingFilters([...filtersValues]);
      setAppliedFilters([...filtersValues]);
    }
  }, [isOpen, type, filtersValues]);

  // Handle local filter changes (working filters)
  const handleWorkingFilterChange = (filter: PublishedFilter | DraftFilter) => {
    setWorkingFilters(prevFilters =>
      prevFilters.map(f => (f.field === filter.field ? filter : f))
    );
  };

  // Handle cancel - reset working filters to applied filters
  const handleCancel = () => {
    setWorkingFilters([...appliedFilters]);
    // Reset parent state to applied filters
    appliedFilters.forEach(filter => {
      onChangeFilter(filter);
    });
    onClose();
  };

  // Handle apply - update applied filters and call parent onApply
  const handleApply = () => {
    const updatedFilters = [...workingFilters];
    // First update the parent state with individual filter changes
    updatedFilters.forEach(filter => {
      onChangeFilter(filter);
    });
    // Then trigger the API call with the updated filters
    onApply(updatedFilters);
    // Finally update local state and close
    setAppliedFilters(updatedFilters);
  };

  // Handle clear - reset both working and applied filters
  const handleClear = () => {
    const emptyFilters: Array<PublishedFilter | DraftFilter> = [
      { field: "TEMPLATENAME", values: [] },
      { field: type === "published" ? "PUBLISHEDBY" : "UPDATEDBY", values: [] },
      {
        field: type === "published" ? "PUBLISHEDON" : "UPDATEDAT",
        values: { from: null, to: null },
      },
    ];
    setWorkingFilters(emptyFilters);
  };

  const filtersFooter = () => (
    <div className="flex justify-end gap-4 px-6 py-6">
      <ButtonTertiary label="Cancel" onClick={handleCancel} />
      <ButtonPrimary label="Apply" onClick={handleApply} />
    </div>
  );

  const DateValues = useMemo(() => {
    return getDateFilterField(
      workingFilters,
      type === "published" ? "PUBLISHEDON" : "UPDATEDAT"
    );
  }, [workingFilters, type]);

  const templateOptions = useMemo(() => {
    if (!templateData || !isArray(templateData.names)) {
      return [];
    }
    return removeDuplicatesByName(
      templateData.names.map((item: string, index: number) => ({
        id: `${index}`,
        name: item,
      }))
    );
  }, [templateData]);

  const byOptions = useMemo(() => {
    return removeDuplicatesByName(
      type === "published"
        ? getPublishedByFilterOptions(templateData)
        : getUpdatedByFilterOptions(templateData)
    );
  }, [templateData, type]);
  return (
    <Flyover
      isOpen={isOpen}
      title="Filters"
      unmount
      onClose={handleCancel}
      footer={filtersFooter()}
      footerStyle={"!relative right-0 !bottom-[1.5rem]"}
      className={"md:!w-[25rem]"}
    >
      <button
        className="font-semibold px-3 mb-3 text-brand-urbint-50 active:text-brand-urbint-60 hover:text-brand-urbint-40"
        onClick={handleClear}
      >
        Clear all
      </button>
      <FilterSection
        title="Template Name"
        count={getFiltersCount(workingFilters, "TEMPLATENAME")}
      >
        <MultiSelect
          options={templateOptions}
          value={getFilterField(workingFilters, "TEMPLATENAME")}
          icon={"search"}
          placeholder={"Search for templates"}
          onSelect={(options: any) =>
            handleWorkingFilterChange({
              field: "TEMPLATENAME",
              values: options,
            })
          }
          isSearchable
        />
      </FilterSection>
      <FilterSection
        title={type === "published" ? "Published By" : "Last Updated By"}
        count={getFiltersCount(
          workingFilters,
          type === "published" ? "PUBLISHEDBY" : "UPDATEDBY"
        )}
      >
        <MultiSelect
          options={byOptions}
          value={getFilterField(
            workingFilters,
            type === "published" ? "PUBLISHEDBY" : "UPDATEDBY"
          )}
          icon={"search"}
          placeholder={"Select"}
          onSelect={(options: any) =>
            handleWorkingFilterChange({
              field: type === "published" ? "PUBLISHEDBY" : "UPDATEDBY",
              values: options,
            })
          }
          isSearchable
        />
      </FilterSection>
      <FilterSection
        title={type === "published" ? "Published On" : "Last Updated On"}
        count={getFiltersCount(
          workingFilters,
          type === "published" ? "PUBLISHEDON" : "UPDATEDAT"
        )}
      >
        <div className="flex flex-row text-base font-semibold text-neutral-shade-75 justify-between">
          <div className="w-[10.5rem]">
            <label>From</label>
            <InputDateSelect
              icon="calendar"
              placeholder="Select a date"
              selectedDate={DateValues.from ? new Date(DateValues.from) : null}
              onDateChange={date => {
                handleWorkingFilterChange({
                  field: type === "published" ? "PUBLISHEDON" : "UPDATEDAT",
                  values: { from: date, to: date ? new Date() : null },
                });
              }}
              maxDate={new Date()}
              dateFormat={"MM-dd-yyyy"}
            />
          </div>
          <div className="w-[10.5rem]">
            <label>To</label>
            <InputDateSelect
              icon="calendar"
              placeholder="Select a date"
              disabled={DateValues.from === null}
              selectedDate={DateValues.to ? new Date(DateValues.to) : null}
              onDateChange={date => {
                handleWorkingFilterChange({
                  field: type === "published" ? "PUBLISHEDON" : "UPDATEDAT",
                  values: { from: DateValues.from, to: date },
                });
              }}
              minDate={DateValues.from} // Set minDate to From Date
              maxDate={new Date()}
              dateFormat={"MM-dd-yyyy"}
            />
          </div>
        </div>
      </FilterSection>
    </Flyover>
  );
};

export default MainFilters;
