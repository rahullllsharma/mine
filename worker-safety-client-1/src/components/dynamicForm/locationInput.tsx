import type { UserFormMode } from "../templatesComponents/customisedForm.types";
import { useState } from "react";
import { BodyText } from "@urbint/silica";
import { Foooter } from "@/components/dynamicForm/index";
import { InputRaw } from "@/components/forms/Basic/Input";
import Switch from "@/components/switch/Switch";
import { WidgetCheckbox } from "@/components/dynamicForm/WidgetCheckbox";
import { Checkbox } from "../forms/Basic/Checkbox";

// type ResponseOption =
//   | "google_api_search"
//   | "manual_address_input"
//   | "lat_lon"
//   | "auto_populate_current_location";

interface FormState {
  title: string;
  is_mandatory: boolean;
  comments_allowed: boolean;
  attachments_allowed: boolean;
  include_in_widget: boolean;
  validation: string[];
  user_value: boolean | null;
  pre_population_rule_name: null;
  user_comments: string | null;
  user_attachments: File[] | null;
  is_show_map_preview: boolean;
}

type Props = {
  initialState?: FormState;
  onAdd: (value: any) => void;
  onClose: () => void;
  disabled?: boolean;
  mode?: UserFormMode;
};

const FormComponent = (props: Props): JSX.Element => {
  const [formState, setFormState] = useState<FormState>(
    props.initialState || {
      title: "",
      is_mandatory: false,
      comments_allowed: false,
      attachments_allowed: false,
      include_in_widget: false,
      validation: [],
      user_value: null,
      pre_population_rule_name: null,
      user_comments: null,
      user_attachments: null,
      is_show_map_preview: false,
    }
  );
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
        <div className="flex items-center gap-2">
          <BodyText>Show map preview</BodyText>
          <Switch
            title={`Show map preview`}
            stateOverride={formState.is_show_map_preview}
            onToggle={() =>
              handleInputChange(
                "is_show_map_preview",
                !formState.is_show_map_preview
              )
            }
            isDisabled={props.disabled}
          />
        </div>
        <div className="flex gap-4">
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
        disabled={props.disabled || formState.title.trim().length === 0}
        onAdd={() => props.onAdd(formState)}
        onClose={props.onClose}
        mode={props.mode}
      />
    </>
  );
};

export default FormComponent;
