import type {
  CheckboxQuestionPropertiesType,
  PrePopulationOptionType,
  CheckboxFormProps,
} from "../templatesComponents/customisedForm.types";
import { useState, useMemo, useContext } from "react";
import { BodyText, ComponentLabel } from "@urbint/silica";
import { Checkbox } from "@/components/forms/Basic/Checkbox";
import { Foooter, RepeatSectionContext } from "@/components/dynamicForm/index";
import FieldRadioGroup from "@/components/shared/field/fieldRadioGroup/FieldRadioGroup";
import { prePopulationOptions } from "@/utils/customisedFormUtils/customisedForm.constants";
import { InputRaw } from "@/components/forms/Basic/Input";
import { isValidHttpUrl } from "@/components/templatesComponents/customisedForm.utils";
import { WidgetCheckbox } from "@/components/dynamicForm/WidgetCheckbox";

const initialState: CheckboxQuestionPropertiesType = {
  title: "",
  pre_population_rule_name: null,
  is_mandatory: false,
  comments_allowed: false,
  attachments_allowed: false,
  include_in_widget: false,
  user_value: [],
  user_comments: null,
  user_attachments: null,
  choice_type: "single_choice",
  options: [],
};

const CheckboxComponent = ({
  initialState: init,
  onAdd,
  onClose,
  disabled,
}: CheckboxFormProps): JSX.Element => {
  const [state, setState] = useState<CheckboxQuestionPropertiesType>(
    () => init || initialState
  );

  const isRepeatableSection = useContext(RepeatSectionContext);

  const validateForm = (formState: CheckboxQuestionPropertiesType): boolean => {
    if (!formState.title.trim()) return false;
    // Validate URL and display text if URL is provided in first option
    if (formState.options && formState.options.length > 0) {
      const firstOption = formState.options[0];
      if (firstOption.url) {
        if (!isValidHttpUrl(firstOption.url)) return false;
        if (!firstOption.url_display_text?.trim()) return false;
      }
    }

    return true;
  };

  // const isValid = validateForm();
  const isValidForm = useMemo(() => validateForm(state), [state]);

  const handleChange = <K extends keyof CheckboxQuestionPropertiesType>(
    key: K,
    value: CheckboxQuestionPropertiesType[K]
  ) => {
    setState(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleUrlChange = (url: string) => {
    setState(prev => {
      const options =
        prev.options.length > 0
          ? [...prev.options]
          : [{ value: "1", label: "", url: "", url_display_text: "" }];
      options[0] = { ...options[0], url };
      return { ...prev, options };
    });
  };

  const handleUrlDisplayTextChange = (url_display_text: string) => {
    setState(prev => {
      const options =
        prev.options.length > 0
          ? [...prev.options]
          : [{ value: "1", label: "", url: "", url_display_text: "" }];
      options[0] = { ...options[0], url_display_text };
      return { ...prev, options };
    });
  };

  return (
    <>
      <div className="flex flex-col gap-4 p-4">
        <div className="flex flex-col gap-2">
          <ComponentLabel className="mb-2">
            Question
            <span className="text-black ml-1">*</span>
          </ComponentLabel>
          <InputRaw
            placeholder="Enter your question"
            value={state.title}
            onChange={value => handleChange("title", value)}
            disabled={disabled}
          />
        </div>
        <div className="flex flex-col gap-4">
          <div className="flex gap-2 mt-2">
            <InputRaw
              label="URL"
              placeholder="https://example.com"
              value={state.options.length > 0 ? state.options[0].url || "" : ""}
              onChange={handleUrlChange}
              disabled={disabled}
            />
            <InputRaw
              label="URL Display Text"
              placeholder="Display text for the link"
              value={
                state.options.length > 0
                  ? state.options[0].url_display_text || ""
                  : ""
              }
              onChange={handleUrlDisplayTextChange}
              disabled={disabled}
            />
          </div>
        </div>
        {!isRepeatableSection && (
          <FieldRadioGroup
            label="Pre Population"
            options={prePopulationOptions}
            defaultOption={
              prePopulationOptions.find(
                p => p.value === (state.pre_population_rule_name ?? "None")
              ) || prePopulationOptions[0]
            }
            onSelect={pop =>
              handleChange(
                "pre_population_rule_name",
                pop === "None" ? null : (pop as PrePopulationOptionType)
              )
            }
            readOnly={disabled}
          />
        )}
        <div className="flex justify-between pt-4 border-gray-200 border-t divide-brand-gray-2">
          <label className="flex items-center gap-2">
            <Checkbox
              checked={!!state.is_mandatory}
              onClick={() => handleChange("is_mandatory", !state.is_mandatory)}
              disabled={disabled}
            />
            <BodyText className="text-sm">Mandatory</BodyText>
          </label>
          <label className="flex items-center gap-2">
            <Checkbox
              checked={!!state.comments_allowed}
              onClick={() =>
                handleChange("comments_allowed", !state.comments_allowed)
              }
              disabled={disabled}
            />
            <BodyText className="text-sm">Comments</BodyText>
          </label>
          <label className="flex items-center gap-2">
            <Checkbox
              checked={!!state.attachments_allowed}
              onClick={() =>
                handleChange("attachments_allowed", !state.attachments_allowed)
              }
              disabled={disabled}
            />
            <BodyText className="text-sm">Attachments</BodyText>
          </label>
          <WidgetCheckbox
            checked={!!state.include_in_widget}
            disabled={disabled}
            onToggle={value => handleChange("include_in_widget", value)}
          />
        </div>
      </div>
      <Foooter
        onAdd={() => onAdd(state)}
        onClose={onClose}
        disabled={!isValidForm || disabled}
      />
    </>
  );
};

export default CheckboxComponent;
