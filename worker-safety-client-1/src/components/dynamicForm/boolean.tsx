import type { RadioGroupOption } from "@/components/shared/radioGroup/RadioGroup";
import type { UserFormMode } from "../templatesComponents/customisedForm.types";
import React, { useEffect, useMemo, useState, useContext } from "react";
import { InputRaw } from "@/components/forms/Basic/Input";
import FieldRadioGroup from "@/components/shared/field/fieldRadioGroup/FieldRadioGroup";
import { Foooter, RepeatSectionContext } from "@/components/dynamicForm/index";
import { prePopulationOptions } from "@/utils/customisedFormUtils/customisedForm.constants";
import { WidgetCheckbox } from "@/components/dynamicForm/WidgetCheckbox";
import { Checkbox } from "../forms/Basic/Checkbox";

type toggleStyle = "text" | "simple" | "thums";

type toggleOptions = {
  label: string;
  value: boolean;
};
interface FormState {
  title: string;
  hint_text: string;
  toggle_style: toggleStyle;
  toggle_options: toggleOptions[];
  is_mandatory: boolean;
  attachments_allowed: boolean;
  comments_allowed: boolean;
  user_value: boolean | null;
  pre_population_rule_name: null;
  user_comments: string | null;
  user_attachments: File[] | null;
  include_in_widget: boolean;
}

const toggleStyles: RadioGroupOption[] = [
  { id: 1, value: "text", description: "Toggle with text" },
  { id: 2, value: "simple", description: "Simple toggle" },
  { id: 3, value: "thums", description: "Thumbs up/Thumbs down" },
];

type Props = {
  initialState?: FormState;
  onAdd: (value: any) => void;
  onClose: () => void;
  disabled?: boolean;
  mode?: UserFormMode;
};

const validateForm = (state: FormState): boolean => {
  if (!state.title.trim()) {
    return false;
  }
  if (state.toggle_style === "text") {
    const [trueOption, falseOption] = state.toggle_options;
    if (!trueOption?.label.trim() || !falseOption?.label.trim()) {
      return false;
    }
  }
  return true;
};

const FormComponent = (props: Props): JSX.Element => {
  const [formState, setFormState] = useState<FormState>(
    props.initialState || {
      title: "",
      toggle_options: [
        {
          label: "",
          value: true,
        },
        {
          label: "",
          value: false,
        },
      ],
      hint_text: "",
      toggle_style: "text",
      is_mandatory: false,
      comments_allowed: false,
      attachments_allowed: false,
      user_value: null,
      pre_population_rule_name: null,
      user_comments: null,
      user_attachments: null,
      include_in_widget: false,
    }
  );

  const isRepeatableSection = useContext(RepeatSectionContext);

  const handleInputChange = (
    name: keyof FormState | keyof toggleOptions,
    value: any,
    index?: number
  ) => {
    if (name === "toggle_options" && typeof index === "number") {
      setFormState(prevState => {
        const updatedToggleOptions = [...prevState.toggle_options];
        updatedToggleOptions[index] = {
          ...updatedToggleOptions[index],
          label: value,
        };
        return { ...prevState, toggle_options: [...updatedToggleOptions] };
      });
    } else {
      setFormState(prevState => ({ ...prevState, [name]: value }));
    }
  };

  useEffect(() => {
    setFormState(prevState => {
      const getLabel = (index: number): string => {
        if (formState.toggle_style === "thums") {
          return index === 0 ? "thumsup" : "thumsdown";
        }

        if (formState.toggle_style === "text") {
          return props.initialState?.toggle_style === "text"
            ? props.initialState.toggle_options?.[index]?.label || ""
            : "";
        }

        return prevState.toggle_options[index]?.label || "";
      };

      const updatedToggleOptions = prevState.toggle_options.map((_, index) => ({
        label: getLabel(index),
        value: index === 0,
      }));

      return { ...prevState, toggle_options: updatedToggleOptions };
    });
  }, [formState.toggle_style]);

  const isValidForm = useMemo(() => validateForm(formState), [formState]);

  const getToggleStyleOption = (toggleStyleValue: string): RadioGroupOption => {
    return (
      toggleStyles.find(option => option.value === toggleStyleValue) ||
      toggleStyles[0]
    );
  };

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
        <FieldRadioGroup
          label="Toggle style"
          options={toggleStyles}
          defaultOption={getToggleStyleOption(formState.toggle_style)}
          onSelect={response => handleInputChange("toggle_style", response)}
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
        {formState.toggle_style === "text" && (
          <>
            <div className="font-light">Toggle with text setting</div>
            <div className="flex gap-4">
              <InputRaw
                label="True *"
                placeholder="Yes *"
                value={formState.toggle_options[0]?.label ?? ""}
                onChange={e => handleInputChange("toggle_options", e, 0)}
                disabled={props.disabled}
              />
              <InputRaw
                label="False *"
                placeholder="No *"
                value={formState.toggle_options[1]?.label ?? ""}
                onChange={e => handleInputChange("toggle_options", e, 1)}
                disabled={props.disabled}
              />
            </div>
          </>
        )}

        <div className="border-gray-200 border-t divide-brand-gray-2 pb-4 flex justify-between gap-4 pt-6">
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
        onClose={props.onClose}
        disabled={!isValidForm || props.disabled}
        mode={props.mode}
      />
    </>
  );
};

export default FormComponent;
