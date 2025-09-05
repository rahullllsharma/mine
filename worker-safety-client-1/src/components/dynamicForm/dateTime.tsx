import type { RadioGroupOption } from "@/components/shared/radioGroup/RadioGroup";
import type { UserFormMode } from "../templatesComponents/customisedForm.types";
import React, { useMemo, useState, useContext } from "react";
import { InputRaw } from "@/components/forms/Basic/Input";
import FieldRadioGroup from "@/components/shared/field/fieldRadioGroup/FieldRadioGroup";
import { Foooter, RepeatSectionContext } from "@/components/dynamicForm/index";
import { prePopulationOptions } from "@/utils/customisedFormUtils/customisedForm.constants";
import { useWidgetCount } from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import { Checkbox } from "../forms/Basic/Checkbox";

type DateResponseType =
  | "manual_input"
  | "auto_populate_current_date"
  | "calendar";

type TimeResponseType = "auto_populate_current_time" | "manual_input";

type Option = "date_time" | "date_only" | "time_only";

type DateType = "single_date" | "date_range";

type Validation = "allow_future_date" | "allow_past_date";

type ValidationTime = "allow_future_time" | "allow_past_time";

interface FormState {
  title: string;
  hint_text?: string;
  is_mandatory: boolean;
  selected_type: Option;
  date_response_type: DateResponseType;
  date_options: DateType;
  date_type: DateType;
  date_validation?: Validation;
  time_validation?: ValidationTime;
  time_response_type: TimeResponseType;
  user_value: boolean | null;
  pre_population_rule_name: null;
  include_in_widget: boolean;
  user_comments: string | null;
  user_attachments: File[] | null;
}

const options: RadioGroupOption<Option>[] = [
  { id: 1, value: "date_time", description: "Date & Time" },
  { id: 2, value: "date_only", description: "Date only" },
  { id: 3, value: "time_only", description: "Time only" },
];

const dateResponseOptions: RadioGroupOption<DateResponseType>[] = [
  {
    id: 1,
    value: "auto_populate_current_date",
    description: "Auto Populate Current Date",
  },
  { id: 2, value: "manual_input", description: "Manual Input - Text Box" },
  { id: 3, value: "calendar", description: "Calendar" },
];

const timeResponseOptions: RadioGroupOption<TimeResponseType>[] = [
  {
    id: 1,
    value: "auto_populate_current_time",
    description: "Auto Populate Current Time",
  },
  { id: 2, value: "manual_input", description: "Manual Input - Text Box" },
];

const dateTypeOptions: RadioGroupOption<DateType>[] = [
  { id: 1, value: "single_date", description: "Single Date" },
  { id: 2, value: "date_range", description: "Date Range" },
];

const dateValidationsOptions: RadioGroupOption<Validation>[] = [
  { id: 1, value: "allow_past_date", description: "Allow past date" },
  { id: 2, value: "allow_future_date", description: "Allow future date" },
];

const timeValidationsOptions: RadioGroupOption<ValidationTime>[] = [
  { id: 1, value: "allow_past_time", description: "Allow past time" },
  { id: 2, value: "allow_future_time", description: "Allow future time" },
];

type Props = {
  initialState?: FormState;
  onAdd: (value: any) => void;
  onClose: () => void;
  disabled?: boolean;
  mode?: UserFormMode;
};

const validateForm = (state: FormState): boolean => {
  let isValid = false;
  if (state.title) {
    isValid = true;
  }
  return isValid;
};
const FormComponent = (props: Props) => {
  const [formState, setFormState] = useState<FormState>(
    props.initialState || {
      title: "",
      selected_type: "date_time",
      is_mandatory: false,
      date_response_type: "manual_input",
      date_options: "single_date",
      date_type: "single_date",
      time_response_type: "manual_input",
      user_value: null,
      pre_population_rule_name: null,
      include_in_widget: false,
      user_comments: null,
      user_attachments: null,
    }
  );
  const isRepeatableSection = useContext(RepeatSectionContext);
  const {
    widgetCount,
    maxWidgetCount,
    incrementWidgetCount,
    decrementWidgetCount,
  } = useWidgetCount();

  const renderDateResponseType = useMemo(() => {
    if (
      formState.selected_type === "date_time" ||
      formState.selected_type === "date_only"
    ) {
      return (
        <FieldRadioGroup
          label="Date respond type"
          options={dateResponseOptions}
          defaultOption={dateResponseOptions.find(
            d => d.value === formState.date_response_type
          )}
          onSelect={response =>
            handleInputChange("date_response_type", response)
          }
          readOnly={props.disabled}
        />
      );
    }
    return null;
  }, [formState.selected_type]);

  const renderTimeResponseType = useMemo(() => {
    if (
      formState.selected_type === "date_time" ||
      formState.selected_type === "time_only"
    ) {
      return (
        <FieldRadioGroup
          label="Time respond type"
          options={timeResponseOptions}
          defaultOption={timeResponseOptions.find(
            t => t.value === formState.time_response_type
          )}
          onSelect={response =>
            handleInputChange("time_response_type", response)
          }
          readOnly={props.disabled}
        />
      );
    }
    return null;
  }, [formState.selected_type]);

  const renderDateType = useMemo(() => {
    if (
      formState.selected_type === "date_time" ||
      formState.selected_type === "date_only"
    ) {
      return (
        <FieldRadioGroup
          label="Date"
          options={dateTypeOptions}
          defaultOption={dateTypeOptions.find(
            d => d.value === formState.date_type
          )}
          onSelect={response => handleInputChange("date_type", response)}
          readOnly={props.disabled}
        />
      );
    }
    return null;
  }, [formState.selected_type]);

  const renderDateValidation = useMemo(() => {
    if (
      formState.selected_type === "date_time" ||
      formState.selected_type === "date_only"
    ) {
      return (
        <FieldRadioGroup
          label="Validation"
          options={dateValidationsOptions}
          defaultOption={dateValidationsOptions.find(
            d => d.value === formState.date_validation
          )}
          readOnly={props.disabled}
          onSelect={response => handleInputChange("date_validation", response)}
        />
      );
    }
    return null;
  }, [formState.selected_type, formState]);

  const renderTimeValidation = useMemo(() => {
    if (
      formState.selected_type === "date_time" ||
      formState.selected_type === "time_only"
    ) {
      return (
        <FieldRadioGroup
          label="Validation"
          options={timeValidationsOptions}
          defaultOption={timeValidationsOptions.find(
            d => d.value === formState.time_validation
          )}
          readOnly={props.disabled}
          onSelect={response => handleInputChange("time_validation", response)}
        />
      );
    }
    return null;
  }, [formState.selected_type, formState]);

  const handleInputChange = (name: string, value: any) => {
    // Handle widget count tracking
    if (name === "include_in_widget") {
      if (value && !formState.include_in_widget) {
        incrementWidgetCount();
      } else if (!value && formState.include_in_widget) {
        decrementWidgetCount();
      }
    }
    setFormState(prevState => ({ ...prevState, [name]: value }));
  };
  const isValidForm = useMemo(() => validateForm(formState), [formState]);
  return (
    <>
      <div className="flex flex-col p-4 gap-4">
        <InputRaw
          label="Question *"
          placeholder="Job start time"
          value={formState.title}
          onChange={e => handleInputChange("title", e)}
          disabled={props.disabled}
        />
        <FieldRadioGroup
          label="Date & time options"
          options={options}
          defaultOption={options.find(o => o.value === formState.selected_type)}
          onSelect={response => handleInputChange("selected_type", response)}
          readOnly={props.disabled}
        />
        {renderDateResponseType}
        {renderDateType}
        {renderDateValidation}
        {formState.selected_type === "date_time" && (
          <span className="border-brand-gray-40 border-t divide-brand-gray-2  flex  pt-2" />
        )}
        {renderTimeResponseType}
        {renderTimeValidation}
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
                response === "None" ? null : response
              );
            }}
            readOnly={props.disabled}
          />
        )}
        <div className="border-brand-gray-40 border-t divide-brand-gray-2  flex  pt-2 gap-4">
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
            checked={formState.include_in_widget}
            onClick={() =>
              handleInputChange(
                "include_in_widget",
                !formState.include_in_widget
              )
            }
            disabled={
              props.disabled ||
              (!formState.include_in_widget && widgetCount >= maxWidgetCount)
            }
          >
            <span className="text-brand-gray-80 text-sm">
              Add to widget ({widgetCount}/{maxWidgetCount} added)
            </span>
          </Checkbox>
        </div>
      </div>
      <Foooter
        onAdd={() => {
          props.onAdd(formState);
        }}
        onClose={props.onClose}
        disabled={!isValidForm || props.disabled}
        mode={props.mode}
      />
    </>
  );
};

export default FormComponent;
