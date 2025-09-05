import type { RadioGroupOption } from "@/components/shared/radioGroup/RadioGroup";
import type { UserFormMode } from "../templatesComponents/customisedForm.types";
import React, { useMemo, useState } from "react";
import { BodyText, CaptionText } from "@urbint/silica";
import { InputRaw } from "@/components/forms/Basic/Input";
import FieldRadioGroup from "@/components/shared/field/fieldRadioGroup/FieldRadioGroup";
import { Foooter } from "@/components/dynamicForm/index";
import { WidgetCheckbox } from "@/components/dynamicForm/WidgetCheckbox";
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
  include_in_widget: boolean;
  user_comments: string | null;
  user_attachments: File[] | null;
}

const options: RadioGroupOption<Option>[] = [
  { id: 1, value: "date_time", description: "Date & Time" },
  { id: 2, value: "date_only", description: "Date only" },
];

const dateTypeOptions: RadioGroupOption<DateType>[] = [
  { id: 1, value: "single_date", description: "Single Date" },
  { id: 2, value: "date_range", description: "Date Range" },
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
      include_in_widget: false,
      user_comments: null,
      user_attachments: null,
    }
  );

  const toggleDateResponseType = () => {
    const isAutoPopulateChecked =
      formState.date_response_type === "auto_populate_current_date";
    const inputType = isAutoPopulateChecked
      ? "manual_input"
      : "auto_populate_current_date";
    handleInputChange("date_response_type", inputType);
  };

  const renderDateAutoPopulateOption = useMemo(() => {
    if (
      formState.selected_type === "date_time" ||
      formState.selected_type === "date_only"
    ) {
      const isAutoPopulateChecked =
        formState.date_response_type === "auto_populate_current_date";

      return (
        <div className="mt-4">
          <CaptionText className="text-tiny md:text-sm text-neutral-shade-75 font-semibold mb-2">
            Default value (ad-hoc templates only)
          </CaptionText>
          <Checkbox
            checked={isAutoPopulateChecked}
            onClick={toggleDateResponseType}
            disabled={props.disabled}
          >
            <BodyText className="text-neutral-shade-100 text-base">
              Auto Populate Current Date
            </BodyText>
          </Checkbox>
        </div>
      );
    }
    return null;
  }, [formState.selected_type, formState.date_response_type, props.disabled]);

  const renderDateType = useMemo(() => {
    if (
      formState.selected_type === "date_time" ||
      formState.selected_type === "date_only"
    ) {
      return (
        <>
          <FieldRadioGroup
            label="Display As"
            options={dateTypeOptions}
            defaultOption={dateTypeOptions.find(
              d => d.value === formState.date_type
            )}
            onSelect={response => handleInputChange("date_type", response)}
            readOnly={props.disabled}
            className="mt-4"
          />
        </>
      );
    }
    return null;
  }, [formState.selected_type]);

  const handleInputChange = (name: string, value: any) => {
    setFormState(prevState => ({ ...prevState, [name]: value }));
  };

  const isValidForm = useMemo(() => validateForm(formState), [formState]);

  return (
    <>
      <div className="flex flex-col p-4">
        <h5>Report Date Settings</h5>
        <InputRaw
          label="Label *"
          value={formState.title}
          onChange={e => handleInputChange("title", e)}
          disabled={props.disabled}
        />
        <FieldRadioGroup
          label="Configuration"
          options={options}
          defaultOption={options.find(o => o.value === formState.selected_type)}
          onSelect={response => handleInputChange("selected_type", response)}
          readOnly={props.disabled}
          className="mt-4"
        />
        {renderDateType}
        {renderDateAutoPopulateOption}
        <div className="border-brand-gray-40 border-t divide-brand-gray-2 flex pt-2 mt-4 gap-4">
          <Checkbox
            checked={formState.is_mandatory}
            onClick={() =>
              handleInputChange("is_mandatory", !formState.is_mandatory)
            }
            disabled={props.disabled}
          >
            <BodyText className="text-neutral-shade-100 text-base">
              Mandatory
            </BodyText>
          </Checkbox>
          <WidgetCheckbox
            checked={formState.include_in_widget}
            disabled={props.disabled}
            onToggle={value => handleInputChange("include_in_widget", value)}
          />
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
