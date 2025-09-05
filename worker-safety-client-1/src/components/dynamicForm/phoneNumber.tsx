import type { RadioGroupOption } from "@/components/shared/radioGroup/RadioGroup";
import type { UserFormMode } from "../templatesComponents/customisedForm.types";
import React, { useMemo, useState, useContext } from "react";
import { InputRaw } from "@/components/forms/Basic/Input";
import FieldRadioGroup from "@/components/shared/field/fieldRadioGroup/FieldRadioGroup";
import { Foooter, RepeatSectionContext } from "@/components/dynamicForm/index";
import { prePopulationOptions } from "@/utils/customisedFormUtils/customisedForm.constants";
import { WidgetCheckbox } from "@/components/dynamicForm/WidgetCheckbox";
import { Checkbox } from "../forms/Basic/Checkbox";

type ResponseOption = "auto_populate" | "manual_input";

export interface FormState {
  title: string;
  response_option: ResponseOption | null;
  is_mandatory: boolean;
  defaultValue?: string;
  user_value: string | null;
  pre_population_rule_name: null;
  include_in_widget: boolean;
  user_comments: string | null;
  user_attachments: File[] | null;
}

const responseOptions: RadioGroupOption[] = [
  {
    id: 1,
    value: "auto_populate",
    description: "Auto populate user phone number",
  },
  { id: 2, value: "manual_input", description: "Manual Input" },
];

type Props = {
  initialState?: FormState;
  onAdd: (value: any) => void;
  onClose: () => void;
  disabled?: boolean;
  mode?: UserFormMode;
};

const validateForm = (state: FormState): boolean => {
  let valid = false;
  if (state.title && state.response_option) {
    valid = true;
  }
  return valid;
};
const FormComponent = (props: Props): JSX.Element => {
  const [formState, setFormState] = useState<FormState>(
    props.initialState || {
      title: "",
      response_option: null,
      is_mandatory: false,
      user_value: null,
      pre_population_rule_name: null,
      include_in_widget: false,
      user_comments: null,
      user_attachments: null,
    }
  );
  const isRepeatableSection = useContext(RepeatSectionContext);

  const handleInputChange = (name: keyof FormState, value: any) => {
    setFormState(prevState => ({ ...prevState, [name]: value }));
  };
  const isValidForm = useMemo(() => validateForm(formState), [formState]);
  return (
    <>
      <div className="flex flex-col p-4 gap-4">
        <InputRaw
          label="Question *"
          placeholder="Phone number"
          value={formState.title}
          onChange={e => handleInputChange("title", e)}
          disabled={props.disabled}
        />
        <FieldRadioGroup
          label="Phone respond type"
          options={responseOptions}
          defaultOption={responseOptions.find(
            r => r.value === formState.response_option
          )}
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
        <div className="border-brand-gray-40 border-t divide-brand-gray-2 flex pt-2 gap-4">
          <Checkbox
            checked={formState.is_mandatory}
            onClick={() =>
              handleInputChange("is_mandatory", !formState.is_mandatory)
            }
            disabled={props.disabled}
          >
            <span className="text-brand-gray-80 text-sm">Mandatory</span>
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
        onClose={props.onClose}
        disabled={!isValidForm || props.disabled}
        mode={props.mode}
      />
    </>
  );
};

export default FormComponent;
