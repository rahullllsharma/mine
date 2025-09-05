import type { FormState, Option } from "@/components/dynamicForm/choice";
import type { FieldType, UserFormMode } from "../customisedForm.types";
import cn from "classnames";
import { useEffect, useState } from "react";
import { BodyText, ComponentLabel } from "@urbint/silica";
import { UserFormModeTypes } from "@/components/templatesComponents/customisedForm.types";
import {
  FORM_EVENTS,
  formEventEmitter,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import useCWFFormState from "@/hooks/useCWFFormState";
import RadioGroup from "@/components/shared/radioGroup/RadioGroup";
import CheckboxGroup from "@/components/checkboxGroup/CheckboxGroup";
import { disabledField, isDisabledMode } from "../customisedForm.utils";
import SvgButton from "../ButtonComponents/SvgButton/SvgButton";
import style from "./previewComponents.module.scss";

type Content = {
  type: FieldType;
  properties: FormState;
  id?: string;
};

type Props = {
  content: Content;
  mode: UserFormMode;
  inSummary?: boolean;
  onChange: (value: any) => void;
};

export const RenderChoiceInSummary = (props: {
  properties: FormState;
  localValue: string[];
}): JSX.Element => {
  const { properties, localValue } = props;
  if (properties.choice_type === "multiple_choice") {
    return (
      <div className="flex flex-col gap-2">
        <ComponentLabel className="text-sm font-semibold cursor-auto">
          {properties.title}
        </ComponentLabel>
        <ul className="flex flex-wrap flex-col list-disc pl-4">
          {localValue.map((value, index) => (
            <li key={index}>
              <BodyText className="text-base">{value}</BodyText>
            </li>
          ))}
        </ul>
      </div>
    );
  }
  if (properties.choice_type === "single_choice") {
    return (
      <div className="flex flex-col gap-2">
        <ComponentLabel className="text-sm font-semibold cursor-auto">
          {properties.title}
        </ComponentLabel>
        <BodyText className="text-base">{localValue[0]}</BodyText>
      </div>
    );
  }
  return <span />;
};

const Options = (props: {
  properties: FormState;
  onSelect: (value: string[]) => void;
  mode: UserFormMode;
  localValue: string[];
  error: boolean;
}): JSX.Element => {
  const { properties, onSelect, mode, localValue } = props;
  const options: { value: string; label: string }[] = [...properties.options];

  const onOptionSelection = (value: string) => {
    let selectedValue: string[] = [];
    if (properties.choice_type === "multiple_choice") {
      if (localValue) {
        selectedValue = localValue.includes(value)
          ? localValue.filter((v: string) => v !== value)
          : [...localValue, value];
      } else {
        selectedValue = [value];
      }
    } else {
      selectedValue = [value];
    }
    onSelect(selectedValue);
  };

  if (properties.response_option === "manual_entry") {
    return properties.choice_type === "multiple_choice" ? (
      <CheckboxGroup
        options={options.map(o => ({
          id: o.label,
          name: o.label,
        }))}
        onChange={e => onSelect(e.map(o => o.name))}
        value={
          localValue
            ? options
                .filter(o => localValue?.includes(o.label))
                .map(o => ({
                  id: o.label,
                  name: o.label,
                  isChecked: true,
                }))
            : []
        }
        disabled={disabledField(mode)}
        hasError={props.error}
      />
    ) : (
      <RadioGroup
        direction="col"
        options={options.map(o => ({
          id: o.label as unknown as number,
          value: o.label,
          description: o.label,
        }))}
        defaultOption={
          localValue
            ? options
                .filter(o => localValue?.includes(o.label))
                .map(o => ({
                  id: o.label as unknown as number,
                  value: o.label,
                  description: o.label,
                }))?.[0]
            : null
        }
        onSelect={e => onSelect([e])}
        isDisabled={
          mode === UserFormModeTypes.BUILD ||
          mode === UserFormModeTypes.PREVIEW ||
          mode === UserFormModeTypes.PREVIEW_PROPS
        }
        hasError={props.error}
      />
    );
  } else if (properties.response_option === "image") {
    return (
      <div className="flex flex-wrap gap-4">
        {options.map((option: Option, index: number) => (
          <div
            className={cn(
              "align-middle border-2 flex gap-4 items-center p-2 pr-32 rounded cursor-pointer",
              {
                ["border-brand-urbint-50"]:
                  localValue && localValue.includes(option.label),
              }
            )}
            key={`${option.label}${index}`}
            onClick={() => onOptionSelection(option.label)}
          >
            {option.image_url && (
              <img
                src={option.image_url}
                alt="Selected"
                style={{ height: 60, width: 60 }}
              />
            )}
            <label className=" block md:text-sm text-neutral-shade-75 font-semibold leading-normal">
              {option.label}
            </label>
          </div>
        ))}
      </div>
    );
  }
  return <span />;
};

function Choice(props: Props): JSX.Element {
  const {
    content: { properties },
    mode,
    inSummary,
    onChange,
  } = props;
  const { setCWFFormStateDirty } = useCWFFormState();
  const [isDisabledForm] = useState(isDisabledMode(mode));

  const [error, setError] = useState(false);
  const onSelect = (value: string[]) => {
    setLocalValue(value);
    setCWFFormStateDirty(true);
  };

  const [localValue, setLocalValue] = useState<string[]>(
    properties.user_value ?? []
  );

  useEffect(() => {
    props.onChange(localValue);
  }, [localValue]);

  useEffect(() => {
    const token = formEventEmitter.addListener(
      FORM_EVENTS.SAVE_AND_CONTINUE,
      () => {
        if (localValue.length) {
          setError(false);
          onChange(localValue);
        } else if (properties.is_mandatory) {
          setError(true);
        } else {
          setError(false);
          onChange(localValue);
        }
      }
    );
    return () => {
      token.remove();
    };
  }, [localValue, props.onChange, properties.is_mandatory]);

  useEffect(() => {
    if (error) {
      if (localValue.length) {
        setError(false);
      } else if (properties.is_mandatory) {
        setError(true);
      } else {
        setError(false);
      }
    }
  }, [error, localValue, properties.is_mandatory]);

  return (
    <div
      className={`${style.choiceComponentParent} flex flex-col`}
      id={props.content.id}
    >
      <div>
        <label className=" block md:text-sm text-neutral-shade-75 font-semibold leading-normal mb-2"></label>
        <div className="flex gap-2 mb-1">
          <label className="block text-tiny md:text-sm text-neutral-shade-75 font-semibold mb-1 leading-normal">
            {properties.title}
            {properties.is_mandatory && !inSummary ? "*" : ""}
          </label>
          {properties.include_in_widget && mode === "BUILD" && (
            <div className="text-neutrals-tertiary flex gap-2">
              <SvgButton svgPath={"/assets/CWF/widget.svg"} />
              <BodyText className="text-neutrals-tertiary">Widget</BodyText>
            </div>
          )}
        </div>
        <Options
          properties={properties}
          onSelect={onSelect}
          mode={mode}
          localValue={isDisabledForm ? [] : localValue}
          error={error && properties.is_mandatory}
        />
      </div>
      {error && properties.is_mandatory && (
        <p className="text-red-500 mt-2">This is required</p>
      )}
    </div>
  );
}

export default Choice;
