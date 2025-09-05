import axiosRest from "@/api/restApi";
import { Foooter, RepeatSectionContext } from "@/components/dynamicForm/index";
import { WidgetCheckbox } from "@/components/dynamicForm/WidgetCheckbox";
import { InputRaw } from "@/components/forms/Basic/Input";
import FieldRadioGroup from "@/components/shared/field/fieldRadioGroup/FieldRadioGroup";
import FieldSelect from "@/components/shared/field/fieldSelect/FieldSelect";
import type { RadioGroupOption } from "@/components/shared/radioGroup/RadioGroup";
import type { SelectOption } from "@/components/shared/select/Select";
import IngestOptionItems from "@/graphql/queries/IngestOptionItems.gql";
import useRestQuery from "@/hooks/useRestQuery";
import { prePopulationOptions } from "@/utils/customisedFormUtils/customisedForm.constants";
import { useQuery } from "@apollo/client";
import { useContext, useEffect, useMemo, useState } from "react";
import { Checkbox } from "../forms/Basic/Checkbox";
import Button from "../shared/button/Button";
import type {
  FetchFromSourceApiDetails,
  UserFormMode,
} from "../templatesComponents/customisedForm.types";
import type { DataSourceColumn, RestDataSource } from "./dropdown.types";
import { ResponseOption } from "./dropdown.types";

const INITIAL_FORM_STATE: FormState = {
  title: "",
  hint_text: "",
  response_option: ResponseOption.ManualEntry,
  options: [],
  multiple_choice: false,
  include_other_option: false,
  include_NA_option: false,
  include_other_input_box: false,
  user_other_value: "",
  is_mandatory: false,
  comments_allowed: false,
  attachments_allowed: false,
  user_value: null,
  pre_population_rule_name: null,
  user_comments: null,
  user_attachments: null,
  data_source_id: undefined,
  data_source_name: undefined,
  data_source_column: undefined,
  api_details: undefined,
};

interface Option {
  value: string;
  label: string;
}

export interface FormState {
  title: string;
  hint_text: string;
  response_option: ResponseOption;
  options: Option[];
  multiple_choice: boolean;
  include_other_option: boolean;
  include_NA_option: boolean;
  include_other_input_box: boolean;
  user_other_value: string | null;
  is_mandatory: boolean;
  comments_allowed: boolean;
  attachments_allowed: boolean;
  include_in_widget?: boolean;
  defaultValue?: string[];
  user_value: string[] | null;
  pre_population_rule_name: string | null;
  user_comments: string | null;
  user_attachments: File[] | null;
  data_source_id?: string;
  data_source_name?: string;
  data_source_column?: string;
  api_details?: FetchFromSourceApiDetails | any;
}

const responseOptions: RadioGroupOption[] = [
  { id: 1, value: ResponseOption.ManualEntry, description: "Manually entry" },
  {
    id: 2,
    value: ResponseOption.Fetch,
    description: "Fetch from imported data source",
  },
];

type Props = {
  initialState?: FormState;
  onAdd: (value: FormState) => void;
  onClose: () => void;
  disabled?: boolean;
  mode?: UserFormMode;
};

const FormComponent = (props: Props) => {
  const [formState, setFormState] = useState<FormState>(
    props.initialState || INITIAL_FORM_STATE
  );
  const isRepeatableSection = useContext(RepeatSectionContext);

  // Fetch available data sources via REST (pattern aligned with other GET usage)
  const { data: restDataSources } = useRestQuery<
    RestDataSource[] | { results: RestDataSource[] }
  >({
    key: ["uploads", "data-sources"],
    endpoint: "/uploads/data-sources/",
    axiosInstance: axiosRest,
    queryOptions: {
      staleTime: 0,
      cacheTime: 0,
    },
  });

  // Fetch data items when data source and column are selected
  const { data: { ingestOptionItems = { items: [] } } = {} } = useQuery(
    IngestOptionItems,
    {
      variables: { key: formState.data_source_id },
      skip: !formState.data_source_id || !formState.data_source_column,
    }
  );

  // Auto-populate options when data source items are loaded
  useEffect(() => {
    if (
      formState.response_option === ResponseOption.Fetch &&
      formState.data_source_id &&
      formState.data_source_column &&
      ingestOptionItems.items.length > 0
    ) {
      const uniqueValues = new Set<string>();
      const newOptions: Option[] = [];

      ingestOptionItems.items.forEach((item: Record<string, unknown>) => {
        const columnKey = formState.data_source_column ?? "";
        const columnValue = (item as Record<string, unknown>)[columnKey];
        if (
          columnValue &&
          typeof columnValue === "string" &&
          !uniqueValues.has(columnValue)
        ) {
          uniqueValues.add(columnValue);
          newOptions.push({
            value: columnValue,
            label: columnValue,
          });
        }
      });

      // Sort options alphabetically
      newOptions.sort((a, b) => a.label.localeCompare(b.label));

      setFormState(prevState => ({
        ...prevState,
        options: newOptions,
      }));
    }
  }, [
    formState.response_option,
    formState.data_source_id,
    formState.data_source_column,
    ingestOptionItems.items,
  ]);

  const validateForm = (state: FormState): boolean => {
    let valid = false;
    if (state.title.trim().length && state.response_option) {
      if (state.response_option === ResponseOption.ManualEntry) {
        valid =
          state.options.filter(o => !!o.label).length === state.options.length;
      } else if (state.response_option === ResponseOption.Fetch) {
        valid = !!state.data_source_id && !!state.data_source_column;
      }
    }
    return valid;
  };

  // Build api_details in the format required for templates when fetching from source
  const buildApiDetails = (
    datasourceId: string,
    columnName: string
  ): FetchFromSourceApiDetails => ({
    name: "Fetch from source API",
    description: "API to fetch column data from Fetch from source",
    endpoint: `uploads/data-sources/${datasourceId}/columns/${columnName}`,
    method: "GET",
    headers: { "Content-Type": "application/json" },
    request: {},
    response: {},
    value_key: columnName,
    label_key: columnName,
  });

  const handleInputChange = <K extends keyof FormState>(
    name: K,
    value: FormState[K]
  ) => {
    setFormState(prevState => ({ ...prevState, [name]: value }));

    if (name === "include_other_option") {
      if (value) {
        addOption({ value: "other", label: "Other" });
      } else {
        // find index of option where value is "other"
        // and remove it
        const index = formState.options.findIndex(o => o.value === "other");
        if (index !== -1) {
          removeOption(index);
        }
      }
    }
    if (name === "include_NA_option") {
      if (value) {
        addOption({ value: "na", label: "N/A" });
      } else {
        // find index of option where value is "na"
        // and remove it
        const index = formState.options.findIndex(o => o.value === "na");
        if (index !== -1) {
          removeOption(index);
        }
      }
    }

    // Reset data source fields when switching to manual entry
    if (name === "response_option" && value === ResponseOption.ManualEntry) {
      setFormState(prevState => ({
        ...prevState,
        data_source_id: INITIAL_FORM_STATE.data_source_id,
        data_source_name: INITIAL_FORM_STATE.data_source_name,
        data_source_column: INITIAL_FORM_STATE.data_source_column,
        api_details: INITIAL_FORM_STATE.api_details,
      }));
    }

    // Reset include_NA_option when switching away from manual entry
    if (name === "response_option" && value !== ResponseOption.ManualEntry) {
      setFormState(prevState => ({
        ...prevState,
        include_NA_option: false,
      }));
      // find index of option where value is "na"
      // and remove it
      const index = formState.options.findIndex(o => o.value === "na");
      if (index !== -1) {
        removeOption(index);
      }
    }
  };

  const addOption = (_options?: { value?: string; label?: string }) => {
    const newOption = {
      value: _options?.value || String(formState.options.length),
      label: _options?.label || "",
    };
    handleInputChange("options", [...formState.options, newOption]);
  };

  const removeOption = (index: number) => {
    const updatedOptions = formState.options.filter((_, i) => i !== index);
    handleInputChange("options", updatedOptions);
  };

  const checkExtraOption = (options: Option[], key: string): boolean => {
    for (const option of options) {
      if (option.value === key) {
        return true;
      }
    }
    return false;
  };

  const handleOptionLabelChange = (index: number, label: string) => {
    const updatedOptions = formState.options.map((option, i) =>
      i === index
        ? {
            ...option,
            label,
            // , value: label
          }
        : option
    );
    handleInputChange("options", updatedOptions);
  };

  const handleOptionLabelBlur = (index: number) => {
    const updatedOptions = formState.options.map((option, i) =>
      i === index
        ? {
            ...option,
            value: option.label,
          }
        : option
    );
    handleInputChange("options", updatedOptions);
  };

  // Normalize REST response shape (supports array or { results: [] })
  const dataSourcesList: RestDataSource[] = Array.isArray(restDataSources)
    ? (restDataSources as RestDataSource[])
    : (restDataSources?.results as RestDataSource[]) || [];

  // Get selected data source
  const selectedDataSource = dataSourcesList.find(
    (option: RestDataSource) => option.id === formState.data_source_id
  );

  // Convert data sources to select options
  const dataSourceOptions: SelectOption[] = dataSourcesList.map(
    (option: RestDataSource) => ({
      id: option.id,
      name: option.name,
    })
  );

  // Convert columns to select options
  const columnOptions: SelectOption[] =
    (selectedDataSource?.columns || []).map((column: DataSourceColumn) => {
      if (typeof column === "string") {
        return { id: String(column), name: String(column) };
      }
      const attr = column.attribute || column.name;
      return { id: String(attr), name: String(attr) };
    }) || [];

  // Create clean form state for submission - only include data source fields when response_option is fetch_from_imported_data
  const getSubmissionFormState = (): FormState => {
    if (formState.response_option === ResponseOption.Fetch) {
      return formState; // Include all fields including data source fields
    } else {
      // Exclude data source fields for manual entry
      const {
        data_source_id: _data_source_id,
        data_source_name: _data_source_name,
        data_source_column: _data_source_column,
        ...cleanState
      } = formState;
      return cleanState;
    }
  };

  const isValidForm = useMemo(() => validateForm(formState), [formState]);
  return (
    <>
      <div className="flex flex-col p-4 gap-4">
        <InputRaw
          label="Question *"
          placeholder="Enter your question"
          value={formState.title}
          onChange={e => handleInputChange("title", e)}
          disabled={props.disabled}
        />
        <InputRaw
          label="Hint text"
          placeholder="Enter your Hint"
          value={formState.hint_text}
          onChange={e => handleInputChange("hint_text", e)}
          disabled={props.disabled}
        />
        <FieldRadioGroup
          label="Response Option"
          options={responseOptions}
          defaultOption={responseOptions.find(
            r => r.value === formState.response_option
          )}
          onSelect={response =>
            handleInputChange("response_option", response as ResponseOption)
          }
          readOnly={props.disabled}
        />

        {formState.response_option === ResponseOption.Fetch && (
          <div className="text-neutral-shade-75 rounded font-inter font-normal text-base leading-[130%] tracking-[0%]">
            Populate dropdown options by selecting a data source and column.
          </div>
        )}

        {/* Data source and column selection */}
        {formState.response_option === ResponseOption.Fetch && (
          <div className="flex flex-col gap-4">
            <FieldSelect
              htmlFor="data-source"
              label="Data Source *"
              placeholder="Select a data source"
              options={dataSourceOptions}
              defaultOption={dataSourceOptions.find(
                opt => opt.id === formState.data_source_id
              )}
              onSelect={(option: SelectOption) =>
                setFormState(prev => {
                  const selected = dataSourcesList.find(
                    ds => ds.id === String(option.id)
                  );
                  const resolvedName =
                    selected?.name || String(option.name ?? "");
                  return {
                    ...prev,
                    data_source_id: String(option.id),
                    data_source_name: resolvedName,
                    data_source_column: undefined,
                    api_details: undefined,
                  };
                })
              }
              readOnly={props.disabled}
            />

            {formState.data_source_id && (
              <FieldSelect
                htmlFor="source-column"
                label="Source Column *"
                placeholder="Select a column name"
                options={columnOptions}
                defaultOption={columnOptions.find(
                  opt => opt.id === formState.data_source_column
                )}
                onSelect={(option: SelectOption) =>
                  setFormState(prev => {
                    const columnName = String(option.id);
                    const dsId = prev.data_source_id
                      ? String(prev.data_source_id)
                      : "";
                    const next: FormState = {
                      ...prev,
                      data_source_column: columnName,
                    } as FormState;
                    if (dsId && columnName) {
                      next.api_details = buildApiDetails(dsId, columnName);
                    }
                    return next;
                  })
                }
                readOnly={props.disabled}
              />
            )}

            {/* Show loaded options count */}
            {formState.options.length > 0 && (
              <div className="text-sm text-neutral-shade-75">
                Loaded {formState.options.length} unique options from the
                selected data source.
              </div>
            )}
          </div>
        )}

        {!isRepeatableSection && (
          <FieldRadioGroup
            label="Pre Population"
            options={prePopulationOptions}
            defaultOption={
              prePopulationOptions.find(
                option => option.value === formState.pre_population_rule_name
              ) || prePopulationOptions[0]
            }
            onSelect={response => {
              handleInputChange(
                "pre_population_rule_name",
                response === "None" ? null : (response as string)
              );
            }}
            readOnly={props.disabled}
          />
        )}

        {/* Manual options section - only show for manual entry */}
        {formState.response_option === ResponseOption.ManualEntry && (
          <>
            <div className="border-gray-200 border-b divide-brand-gray-2 pb-4 flex flex-col gap-4">
              {formState.options.map((option, index) => (
                <div key={option.value} className="flex flex-col">
                  {option.value === "other" || option.value === "na" ? null : (
                    <div
                      className="flex self-end"
                      style={{ marginBottom: -20 }}
                    >
                      <Button
                        label="Remove Option"
                        iconStart="minus_circle_outline"
                        className="text-sm md:text-sm text-neutral-shade-75 font-semibold mb-2 leading-normal z-10"
                        onClick={() => removeOption(index)}
                        disabled={props.disabled}
                      />
                    </div>
                  )}
                  <InputRaw
                    label={`Option ${index + 1}*`}
                    placeholder="Option label"
                    value={option.label}
                    onChange={e => handleOptionLabelChange(index, e)}
                    onBlur={() => handleOptionLabelBlur(index)}
                    disabled={props.disabled}
                  />
                </div>
              ))}
            </div>

            <Button
              label="Add Option"
              iconStart="plus_square"
              className="text-sm md:text-sm text-neutral-shade-75 font-semibold mb-2 leading-normal self-end"
              onClick={() => addOption()}
              disabled={props.disabled}
            />
          </>
        )}

        <div className="border-gray-200 border-b divide-brand-gray-2 pb-4 flex gap-4">
          <Checkbox
            checked={formState.multiple_choice}
            onClick={() =>
              handleInputChange("multiple_choice", !formState.multiple_choice)
            }
            disabled={props.disabled}
          >
            <span className="text-brand-gray-80 text-sm">
              {"Multiple Choice"}
            </span>
          </Checkbox>
          <Checkbox
            checked={checkExtraOption(formState.options, "other")}
            onClick={() =>
              handleInputChange(
                "include_other_option",
                !formState.include_other_option
              )
            }
            disabled={props.disabled}
          >
            <span className="text-brand-gray-80 text-sm">
              {"Include 'Other' in response"}
            </span>
          </Checkbox>
          {formState.response_option === ResponseOption.ManualEntry && (
            <Checkbox
              checked={formState.include_NA_option}
              onClick={() =>
                handleInputChange(
                  "include_NA_option",
                  !formState.include_NA_option
                )
              }
              disabled={props.disabled}
            >
              <span className="text-brand-gray-80 text-sm">
                {"Include 'N/A' in response"}
              </span>
            </Checkbox>
          )}
        </div>

        <div className="flex justify-between">
          <Checkbox
            checked={formState.is_mandatory}
            onClick={() =>
              handleInputChange("is_mandatory", !formState.is_mandatory)
            }
            disabled={props.disabled}
          >
            <span className="text-brand-gray-80 text-sm">Mandatory</span>
          </Checkbox>
          <Checkbox
            checked={formState.comments_allowed}
            onClick={() =>
              handleInputChange("comments_allowed", !formState.comments_allowed)
            }
            disabled={props.disabled}
          >
            <span className="text-brand-gray-80 text-sm">Comments</span>
          </Checkbox>
          <Checkbox
            checked={formState.attachments_allowed}
            onClick={() =>
              handleInputChange(
                "attachments_allowed",
                !formState.attachments_allowed
              )
            }
            disabled={props.disabled}
          >
            <span className="text-brand-gray-80 text-sm">Attachment</span>
          </Checkbox>
          <WidgetCheckbox
            checked={formState.include_in_widget || false}
            disabled={props.disabled}
            onToggle={value => handleInputChange("include_in_widget", value)}
          />
        </div>
      </div>
      <Foooter
        onAdd={() => props.onAdd(getSubmissionFormState())}
        onClose={props.onClose}
        disabled={!isValidForm || props.disabled}
        mode={props.mode}
      />
    </>
  );
};

export default FormComponent;
