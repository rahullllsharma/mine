import type { FormState } from "@/components/dynamicForm/dropdown";
import type {
  DropDownValue,
  FieldType,
  OptionValue,
  UserFormMode,
} from "@/components/templatesComponents/customisedForm.types";
import { BodyText, ComponentLabel } from "@urbint/silica";
import { identity } from "fp-ts/function";
import { useEffect, useState } from "react";
import { InputRaw } from "@/components/forms/Basic/Input/InputRaw";
import { MultiSelect } from "@/components/forms/Basic/MultiSelect";
import { SingleSelect } from "@/components/forms/Basic/SingleSelect";
import SvgButton from "@/components/templatesComponents/ButtonComponents/SvgButton/SvgButton";
import {
  FORM_EVENTS,
  formEventEmitter,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import useCWFFormState from "@/hooks/useCWFFormState";
import { disabledField } from "../customisedForm.utils";

export const RenderDropDownInSummary = (props: {
  properties: FormState;
  localValue: string[];
}): JSX.Element => {
  const { properties, localValue } = props;
  if (properties.multiple_choice) {
    return (
      <div className="flex flex-col gap-2">
        <ComponentLabel className="text-sm font-semibold cursor-auto">
          {properties.title}
        </ComponentLabel>
        <ul className="flex flex-wrap flex-col list-disc pl-4">
          {localValue.map((value, index) => (
            <li key={index}>
              <BodyText className="text-base">
                {value === "other"
                  ? value +
                      (properties.user_other_value &&
                        `: ${properties.user_other_value}`) || ""
                  : value}
              </BodyText>
            </li>
          ))}
        </ul>
      </div>
    );
  }
  if (!properties.multiple_choice) {
    return (
      <div className="flex flex-col gap-2">
        <ComponentLabel className="text-sm font-semibold cursor-auto">
          {properties.title}
        </ComponentLabel>
        <BodyText className="text-base">
          {localValue[0] === "other"
            ? localValue[0] +
                (properties.user_other_value &&
                  `: ${properties.user_other_value}`) || ""
            : localValue[0]}
        </BodyText>
      </div>
    );
  }
  return <span />;
};
type Content = {
  type: FieldType;
  properties: FormState;
  id?: string;
};

type Props = {
  content: Content;
  mode: UserFormMode;
  inSummary?: boolean;
  onChange: (value: DropDownValue) => void;
  onOtherValueChange?: (value: string) => void;
  returnLabelAndValue?: boolean;
};

const isOptionValue = (item: string | OptionValue): item is OptionValue => {
  return (
    typeof item === "object" &&
    item !== null &&
    "value" in item &&
    "label" in item
  );
};

const isStringArray = (value: DropDownValue): value is string[] => {
  return (
    Array.isArray(value) && value.length > 0 && typeof value[0] === "string"
  );
};

const isOptionValueArray = (value: DropDownValue): value is OptionValue[] => {
  return Array.isArray(value) && value.length > 0 && isOptionValue(value[0]);
};

function DropDown(props: Props): JSX.Element {
  const {
    content: { properties },
    inSummary,
    returnLabelAndValue = false,
    mode,
    onOtherValueChange,
  } = props;
  const [localValue, setLocalValue] = useState<DropDownValue>(
    properties.user_value
  );
  const [otherValue, setOtherValue] = useState<string>(
    properties.user_other_value || ""
  );
  const [error, setError] = useState(false);
  const { setCWFFormStateDirty } = useCWFFormState();

  const isOtherSelected = (() => {
    if (returnLabelAndValue && isOptionValueArray(localValue)) {
      return localValue.some(item => item.value === "other");
    } else if (isStringArray(localValue)) {
      return localValue.includes("other");
    }
    return false;
  })();

  const options: OptionValue[] = [...properties.options];
  if (properties.include_other_option) {
    const filteredOptions = options.filter(option => option.value !== "other");
    options.length = 0;
    options.push(...filteredOptions);
    options.push({ value: "other", label: "Other" });
  }

  if (
    properties.include_NA_option &&
    properties.response_option === "manual_entry"
  ) {
    // Check if N/A option already exists to prevent duplicates
    const naExists = options.some(
      option => option.value === "n/a" || option.value === "na"
    );
    if (!naExists) {
      options.push({ value: "n/a", label: "N/A" });
    }
  }

  const onOptionSelection = (value: string) => {
    let selectedValue: DropDownValue = [];

    if (value === "") {
      selectedValue = [];
    } else if (returnLabelAndValue) {
      const selectedOption = options.find(option => option.value === value);
      if (!selectedOption) return;

      if (properties.multiple_choice) {
        if (localValue && isOptionValueArray(localValue)) {
          const isAlreadySelected = localValue.some(
            item => item.value === value
          );

          if (isAlreadySelected) {
            selectedValue = localValue.filter(item => item.value !== value);
          } else {
            selectedValue = [...localValue, selectedOption];
          }
        } else {
          selectedValue = [selectedOption];
        }
      } else {
        selectedValue = [selectedOption];
      }
    } else {
      if (properties.multiple_choice) {
        if (localValue && isStringArray(localValue)) {
          selectedValue = localValue.includes(value)
            ? localValue.filter(v => v !== value)
            : [...localValue, value];
        } else {
          selectedValue = [value];
        }
      } else {
        selectedValue = [value];
      }
    }

    setLocalValue(selectedValue);

    if (value === "other") {
      const hasOther = returnLabelAndValue
        ? isOptionValueArray(selectedValue) &&
          selectedValue.some(item => item.value === "other")
        : isStringArray(selectedValue) && selectedValue.includes("other");

      if (!hasOther) {
        setOtherValue("");
      }
    }

    setCWFFormStateDirty(true);

    if (properties.is_mandatory) {
      const hasValue = selectedValue.length > 0;
      setError(!hasValue);
    } else {
      setError(false);
    }
  };

  const onOptionRemove = (value: string) => {
    if (localValue) {
      let newValue: DropDownValue;

      if (returnLabelAndValue && isOptionValueArray(localValue)) {
        newValue = localValue.filter(item => item.value !== value);
      } else if (isStringArray(localValue)) {
        newValue = localValue.filter(v => v !== value);
      } else {
        newValue = [];
      }

      setLocalValue(newValue);

      if (value === "other") {
        setOtherValue("");
      }

      if (properties.is_mandatory) {
        const hasValue = newValue && newValue.length > 0;
        setError(!hasValue);
      }
    }
  };

  const handleOtherValueChange = (value: string) => {
    setOtherValue(value);
    setCWFFormStateDirty(true);
    onOtherValueChange?.(value);

    if (isOtherSelected && properties.is_mandatory) {
      setError(value.trim() === "");
    }
  };

  useEffect(() => {
    const updateFormData = () => {
      props.onChange(localValue);

      if (props.content && props.content.properties) {
        props.content.properties.user_other_value = otherValue;
      }
    };

    updateFormData();
  }, [localValue, otherValue]);

  useEffect(() => {
    const token = formEventEmitter.addListener(
      FORM_EVENTS.SAVE_AND_CONTINUE,
      () => {
        if (properties.is_mandatory) {
          if (localValue && localValue.length > 0) {
            if (isOtherSelected && otherValue.trim() === "") {
              setError(true);
            } else {
              setError(false);
            }
          } else {
            setError(true);
          }
        } else {
          setError(false);
        }

        props.onChange(localValue || []);
      }
    );
    return () => {
      token.remove();
    };
  }, [localValue, props, properties.is_mandatory, isOtherSelected, otherValue]);

  const getSelectedValues = (): string[] => {
    if (returnLabelAndValue && isOptionValueArray(localValue)) {
      return localValue.map(item => item.value);
    } else if (isStringArray(localValue)) {
      return localValue;
    }
    return [];
  };

  const shouldBeDisabled = inSummary || disabledField(mode ?? "PREVIEW");

  // Custom label with widget icon if include_in_widget is true
  const renderCustomLabel = () => {
    return (
      <div className="flex gap-2">
        <label className="block text-tiny md:text-sm text-neutral-shade-75 font-semibold leading-normal">
          {properties.title +
            (properties.is_mandatory && !inSummary ? "*" : "")}
        </label>
        {properties.include_in_widget && mode === "BUILD" && (
          <div className="text-neutrals-tertiary flex gap-2">
            <SvgButton svgPath={"/assets/CWF/widget.svg"} />
            <BodyText className="text-neutrals-tertiary">Widget</BodyText>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col gap-2" id={props.content.id}>
      {renderCustomLabel()}

      {properties.multiple_choice ? (
        <MultiSelect
          labelClassName="block text-tiny md:text-sm text-neutral-shade-75 font-semibold mb-2 leading-normal"
          label=""
          placeholder={properties.hint_text || "Select a Option"}
          options={options.map((o: OptionValue) => ({
            label: o.label,
            value: o.value,
          }))}
          selected={getSelectedValues()}
          onSelected={onOptionSelection}
          onRemoved={onOptionRemove}
          renderLabel={(s: string) => s}
          optionKey={identity}
          disabled={shouldBeDisabled}
          hasError={error}
        />
      ) : (
        <SingleSelect
          placeholder={properties.hint_text || "Select an option"}
          options={options.map((o: OptionValue) => ({
            label: o.label,
            value: o.value,
          }))}
          selected={getSelectedValues()[0]}
          onSelected={onOptionSelection}
          onClear={() => onOptionSelection("")}
          disabled={shouldBeDisabled}
          hasError={error}
          showFullContent={options.some(option => option.label.length > 50)}
        />
      )}

      {isOtherSelected && (
        <div className="ml-4">
          <InputRaw
            label="Please specify:"
            placeholder="Enter your response"
            value={otherValue}
            onChange={handleOtherValueChange}
            disabled={shouldBeDisabled}
            hasError={error && isOtherSelected && !otherValue.trim()}
          />
        </div>
      )}

      {error && properties.is_mandatory && (
        <div className="text-red-500 mt-2">
          {isOtherSelected && !otherValue.trim()
            ? "Please specify your response for 'Other' option"
            : "This field is required"}
        </div>
      )}
    </div>
  );
}

export default DropDown;
