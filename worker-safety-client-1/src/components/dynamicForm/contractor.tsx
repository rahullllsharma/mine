import type {
  ApiDetails,
  UserFormMode,
} from "@/components/templatesComponents/customisedForm.types";
import React, { useMemo, useState } from "react";
import { InputRaw } from "@/components/forms/Basic/Input";
import { prePopulationOptions } from "@/utils/customisedFormUtils/customisedForm.constants";
import { WidgetCheckbox } from "@/components/dynamicForm/WidgetCheckbox";
import { Checkbox } from "../forms/Basic/Checkbox";
import FieldRadioGroup from "../shared/field/fieldRadioGroup/FieldRadioGroup";
import { Foooter } from "./index";

export const CONTRACTORS_API_DETAILS = {
  name: "Contractors API",
  description: "API to fetch list of contractors",
  endpoint: "/graphql",
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  request: {
    query: `query Contractors {
      contractors {
        id
        name
      }
    }`,
  },
  response: {},
  query: "Contractors",
  response_path: "contractors",
  value_key: "id",
  label_key: "name",
} as const;

interface FormState {
  title: string;
  hint_text?: string;
  is_mandatory: boolean;
  user_value: string[] | null;
  pre_population_rule_name: null;
  options: Array<{ value: string; label: string }>;
  multiple_choice: boolean;
  description: string | null;
  attachments_allowed: boolean;
  comments_allowed: boolean;
  include_in_widget: boolean;
  user_comments: string | null;
  user_attachments: File[] | null;
}

type Props = {
  initialState?: FormState;
  onAdd: (value: FormState & { api_details: ApiDetails }) => void;
  onClose: () => void;
  disabled?: boolean;
  mode?: UserFormMode;
};

const validateForm = (state: FormState): boolean => {
  return !!state.title;
};

const ContractorComponent = (props: Props) => {
  const [formState, setFormState] = useState<FormState>(
    props.initialState || {
      title: "Contractor",
      is_mandatory: false,
      user_value: null,
      pre_population_rule_name: null,
      options: [],
      multiple_choice: false,
      hint_text: "Select a contractor",
      description: null,
      attachments_allowed: false,
      comments_allowed: false,
      include_in_widget: false,
      user_comments: null,
      user_attachments: null,
    }
  );

  const handleInputChange = (
    name: keyof FormState,
    value: string | boolean | null
  ) => {
    setFormState(prevState => ({ ...prevState, [name]: value }));
  };

  const isValidForm = useMemo(() => validateForm(formState), [formState]);

  return (
    <>
      <div className="flex flex-col p-4 gap-4 min-h-[420px]">
        <h5>Contractor Settings</h5>
        <InputRaw
          label="Label *"
          value={formState.title}
          onChange={e => handleInputChange("title", e)}
          disabled={props.disabled}
        />
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
        onAdd={() =>
          props.onAdd({
            ...formState,
            api_details: CONTRACTORS_API_DETAILS,
          })
        }
        onClose={props.onClose}
        disabled={!isValidForm || props.disabled}
        mode={props.mode}
      />
    </>
  );
};

export default ContractorComponent;
