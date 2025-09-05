import type { RadioGroupOption } from "@/components/shared/radioGroup/RadioGroup";
import type {
  InputResponseOption,
  InputTextPropertiesType,
  UserFormMode,
} from "../templatesComponents/customisedForm.types";
import { ActionLabel } from "@urbint/silica";
import { useContext, useMemo, useState } from "react";
import { Foooter, RepeatSectionContext } from "@/components/dynamicForm/index";
import { InputRaw } from "@/components/forms/Basic/Input";
import FieldRadioGroup from "@/components/shared/field/fieldRadioGroup/FieldRadioGroup";
import { prePopulationOptions } from "@/utils/customisedFormUtils/customisedForm.constants";
import { WidgetCheckbox } from "@/components/dynamicForm/WidgetCheckbox";
import { Checkbox } from "../forms/Basic/Checkbox";

const responseOptions: RadioGroupOption[] = [
  {
    id: 1,
    value: "allow_special_characters",
    description: "Plain Text",
  },
  { id: 2, value: "alphanumeric", description: "Alphanumeric" },

  { id: 3, value: "regex", description: "Regex" },
];

const responseValidationOptions: RadioGroupOption[] = [
  { id: 1, value: "short_text", description: "Short Text" },
  { id: 2, value: "long_text", description: "Long Text" },
];

type Props = {
  initialState?: InputTextPropertiesType;
  onAdd: (value: any) => void;
  onClose: () => void;
  disabled?: boolean;
  mode?: UserFormMode;
  onDataChange?: () => void;
};

const validateForm = (state: InputTextPropertiesType) => {
  let valid = false;

  if (state.title.trim()) {
    valid = true;
  }

  return valid;
};

const FormComponent = (props: Props): JSX.Element => {
  const [formState, setFormState] = useState<InputTextPropertiesType>(
    props.initialState || {
      title: "",
      sub_label: "",
      placeholder: "",
      pre_population_rule_name: null,
      hint_text: "",
      input_type: "short_text",
      response_option: "allow_special_characters",
      is_mandatory: false,
      comments_allowed: false,
      attachments_allowed: false,
      include_in_widget: false,
      validation: [],
      user_value: null,
      user_comments: null,
      user_attachments: null,
    }
  );

  const isRepeatableSection = useContext(RepeatSectionContext);

  const isValidForm = useMemo(() => validateForm(formState), [formState]);

  const handleInputChange = (
    name: keyof InputTextPropertiesType,
    value: any
  ) => {
    setFormState(prevState => ({ ...prevState, [name]: value }));

    // Notify parent that data has been entered/changed
    if (props.onDataChange) {
      props.onDataChange();
    }
  };

  const findResponseOptionByFormState = (
    response_option: InputResponseOption
  ): RadioGroupOption => {
    const foundResponseOption = responseOptions.find(
      responseOption => response_option === responseOption.value
    );

    return foundResponseOption || responseOptions[0];
  };

  return (
    <>
      <div className="flex flex-col p-4 gap-4">
        <ActionLabel>Field Settings</ActionLabel>
        <InputRaw
          label="Label *"
          placeholder="Enter a label"
          value={formState.title}
          onChange={e => handleInputChange("title", e)}
          disabled={props.disabled}
        />
        <InputRaw
          label="Sublabel"
          sublabel="Example text that appears below the field's label"
          placeholder="Enter a sublabel"
          value={formState.sub_label || ""}
          onChange={e => handleInputChange("sub_label", e)}
          disabled={props.disabled}
        />
        <InputRaw
          label="Placeholder"
          sublabel="Example text that appears inside the field as guidance"
          placeholder="Enter a placeholder"
          value={formState.placeholder || ""}
          onChange={e => handleInputChange("placeholder", e)}
          disabled={props.disabled}
        />
        <FieldRadioGroup
          label="Input Type"
          options={responseValidationOptions}
          defaultOption={responseValidationOptions[0]}
          onSelect={response => handleInputChange("input_type", response)}
          readOnly={props.disabled}
        />
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
        <FieldRadioGroup
          label="Input validations"
          options={responseOptions}
          defaultOption={
            formState.response_option
              ? findResponseOptionByFormState(formState.response_option)
              : responseOptions[0]
          }
          onSelect={response => handleInputChange("response_option", response)}
          readOnly={props.disabled}
        />
        {formState.response_option === "regex" && (
          <InputRaw
            label="Regex Expression"
            placeholder="Enter Regex Expression"
            value={formState.validation[0] || ""}
            onChange={e => handleInputChange("validation", [e])}
            disabled={props.disabled}
          />
        )}
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
            checked={formState.include_in_widget}
            disabled={props.disabled}
            onToggle={value => handleInputChange("include_in_widget", value)}
          />
        </div>
      </div>
      <Foooter
        onAdd={() => props.onAdd(formState)}
        disabled={!isValidForm || props.disabled}
        onClose={props.onClose}
        mode={props.mode}
        hasDataEntered={formState.title.trim().length > 0}
      />
    </>
  );
};

export default FormComponent;
