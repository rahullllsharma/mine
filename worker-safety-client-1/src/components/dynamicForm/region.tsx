import type {
  RegionFormState,
  UserFormMode,
} from "@/components/templatesComponents/customisedForm.types";
import { useMemo, useState } from "react";
import { InputRaw } from "@/components/forms/Basic/Input";
import { REGIONS_API_DETAILS } from "@/components/templatesComponents/customisedForm.types";
import { prePopulationOptions } from "@/utils/customisedFormUtils/customisedForm.constants";
import { WidgetCheckbox } from "@/components/dynamicForm/WidgetCheckbox";
import { Checkbox } from "../forms/Basic/Checkbox";
import FieldRadioGroup from "../shared/field/fieldRadioGroup/FieldRadioGroup";
import { Foooter } from "./index";

type Props = {
  initialState?: RegionFormState;
  onAdd: (value: RegionFormState) => void;
  onClose: () => void;
  disabled?: boolean;
  mode?: UserFormMode;
};
const ALPHANUMERIC_PATTERN = /^[a-zA-Z0-9]+( [a-zA-Z0-9]+)*$/;

const validateForm = (formState: RegionFormState) => {
  const trimmedTitle = formState.title.trim();
  return trimmedTitle.length > 0 && ALPHANUMERIC_PATTERN.test(trimmedTitle);
};

const RegionComponent = (props: Props) => {
  const [formState, setFormState] = useState<RegionFormState>(
    props.initialState || {
      title: "Region",
      is_mandatory: true,
      user_value: null,
      pre_population_rule_name: null,
      options: [],
      multiple_choice: false,
      hint_text: `Select a region`,
      description: null,
      attachments_allowed: false,
      comments_allowed: false,
      include_in_widget: false,
      user_comments: null,
      user_attachments: null,
      api_details: REGIONS_API_DETAILS,
    }
  );
  const [isTitleTouched, setIsTitleTouched] = useState(false);

  const handleInputChange = (
    name: keyof RegionFormState,
    value: string | boolean | null
  ) => {
    setFormState(prevState => {
      if (name === "title" && typeof value === "string") {
        return {
          ...prevState,
          [name]: value,
          hint_text: `Select a ${value}`,
        };
      } else {
        return {
          ...prevState,
          [name]: value,
        };
      }
    });
    if (name === "title") {
      setIsTitleTouched(true);
    }
  };

  const isValidForm = useMemo(() => validateForm(formState), [formState]);

  return (
    <>
      <div className="flex flex-col p-4 gap-4 min-h-[420px]">
        <h5>Region Settings</h5>
        <InputRaw
          label="Label *"
          value={formState.title}
          onChange={e => handleInputChange("title", e)}
          disabled={props.disabled}
        />
        {isTitleTouched &&
          formState.title.trim().length > 0 &&
          !ALPHANUMERIC_PATTERN.test(formState.title.trim()) && (
            <p className="text-red-500">Must match pattern</p>
          )}

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
        <div className="text-[13px] text-gray-600">
          Work Package forms always pre-populate with the Work Package value
          when available.
        </div>
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

export default RegionComponent;
