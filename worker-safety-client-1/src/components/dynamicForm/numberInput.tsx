import type { RadioGroupOption } from "@/components/shared/radioGroup/RadioGroup";
import type { UserFormMode } from "../templatesComponents/customisedForm.types";
import { useState, useContext } from "react";
import { Foooter, RepeatSectionContext } from "@/components/dynamicForm/index";
import { InputRaw } from "@/components/forms/Basic/Input";
import FieldRadioGroup from "@/components/shared/field/fieldRadioGroup/FieldRadioGroup";
import { prePopulationOptions } from "@/utils/customisedFormUtils/customisedForm.constants";
import { WidgetCheckbox } from "@/components/dynamicForm/WidgetCheckbox";
import { Checkbox } from "../forms/Basic/Checkbox";

type ResponseOption = "allowNegativeNumbers" | "allowDecimals";

export interface FormState {
  title: string;
  response_option: ResponseOption | null;
  hint_text: string;
  description: string;
  is_mandatory: boolean;
  comments_allowed: boolean;
  attachments_allowed: boolean;
  include_in_widget: boolean;
  unit_name: string;
  display_units: boolean;
  validation: string[];
  user_value: boolean | null;
  pre_population_rule_name: null;
  user_comments: string | null;
  user_attachments: File[] | null;
}

const responseOptions: RadioGroupOption[] = [
  {
    id: 1,
    value: "allowNegativeNumbers",
    description: "Allow Negative Numbers",
  },
  { id: 2, value: "allowDecimals", description: "Allow Decimals" },
];

type Props = {
  initialState?: FormState;
  onAdd: (value: any) => void;
  onClose: () => void;
  disabled?: boolean;
  mode?: UserFormMode;
};

const NumberInput = (props: Props): JSX.Element => {
  const [formState, setFormState] = useState<FormState>(
    props.initialState || {
      title: "",
      response_option: "allowNegativeNumbers",
      hint_text: "",
      description: "",
      is_mandatory: false,
      comments_allowed: false,
      attachments_allowed: false,
      include_in_widget: false,
      unit_name: "",
      display_units: false,
      validation: [],
      user_value: null,
      pre_population_rule_name: null,
      user_comments: null,
      user_attachments: null,
    }
  );
  const isRepeatableSection = useContext(RepeatSectionContext);

  const handleInputChange = (name: keyof FormState, value: any) => {
    setFormState(prevState => ({ ...prevState, [name]: value }));
  };
  return (
    <>
      <div className="flex flex-col p-4 gap-4">
        <InputRaw
          label="Question"
          placeholder="Enter a question"
          value={formState.title}
          onChange={e => handleInputChange("title", e)}
          disabled={props.disabled}
        />
        <FieldRadioGroup
          label="Number respond type"
          options={responseOptions}
          defaultOption={
            responseOptions.find(
              option => option.value === formState.response_option
            ) ?? responseOptions[0]
          }
          onSelect={response => handleInputChange("response_option", response)}
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

        <div className="flex flex-col gap-4 mt-4 mb-4 w-1/2">
          <Checkbox
            checked={formState.display_units}
            onClick={() =>
              handleInputChange("display_units", !formState.display_units)
            }
            disabled={props.disabled}
          >
            <span className="text-brand-gray-80 text-sm">Display Units</span>
          </Checkbox>
          {formState.display_units && (
            <InputRaw
              label="Unit Value"
              placeholder="Enter units"
              value={formState.unit_name}
              onChange={e => handleInputChange("unit_name", e)}
              disabled={props.disabled}
            />
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
            checked={formState.include_in_widget}
            disabled={props.disabled}
            onToggle={value => handleInputChange("include_in_widget", value)}
          />
        </div>
      </div>
      <Foooter
        onAdd={() => props.onAdd(formState)}
        disabled={props.disabled || formState.title.trim().length === 0}
        onClose={props.onClose}
        mode={props.mode}
      />
    </>
  );
};

export default NumberInput;
