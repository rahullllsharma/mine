import type { UserFormMode } from "../customisedForm.types";
import { useEffect, useState } from "react";
import { BodyText, ComponentLabel } from "@urbint/silica";
import Switch from "@/components/switch/Switch";
import {
  FORM_EVENTS,
  formEventEmitter,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import useCWFFormState from "@/hooks/useCWFFormState";
import { UserFormModeTypes } from "../customisedForm.types";
import SvgButton from "../ButtonComponents/SvgButton/SvgButton";
import style from "./previewComponents.module.scss";
import ThumbSwitch from "./ThumbSwitch";

const YesOrNo = ({
  content,
  mode,
  inSummary,
  onChange,
}: {
  content: any;
  mode: UserFormMode;
  inSummary?: boolean;
  onChange: (value: any) => void;
}) => {
  const [localValue, setLocalValue] = useState(
    content.properties.user_value ?? false
  );
  const { include_in_widget } = content.properties;
  const [error, setError] = useState(false);
  const { setCWFFormStateDirty } = useCWFFormState();

  const onChangeLocalValue = (value: boolean) => {
    setLocalValue(value);
    setCWFFormStateDirty(true);
  };

  const renderSwitchType = (toggleStyle: string) => {
    switch (toggleStyle) {
      case "text":
        return inSummary ? (
          <div>
            <BodyText className="text-base">
              {localValue ? (
                <BodyText className="text-base">
                  {content.properties.toggle_options[0].label}
                </BodyText>
              ) : (
                <BodyText className="text-base">
                  {content.properties.toggle_options[1].label}
                </BodyText>
              )}
            </BodyText>
          </div>
        ) : (
          <div className={style.yesOrNoComponentParent__textToggle}>
            {localValue ? (
              <p>{content.properties.toggle_options[0].label}</p>
            ) : (
              <p>{content.properties.toggle_options[1].label}</p>
            )}
            <Switch
              stateOverride={localValue}
              onToggle={onChangeLocalValue}
              isDisabled={
                mode === UserFormModeTypes.BUILD ||
                mode === UserFormModeTypes.PREVIEW ||
                mode === UserFormModeTypes.PREVIEW_PROPS
              }
            />
          </div>
        );
      case "simple":
        return (
          <Switch
            stateOverride={localValue}
            onToggle={onChangeLocalValue}
            isDisabled={
              mode === UserFormModeTypes.BUILD ||
              mode === UserFormModeTypes.PREVIEW ||
              mode === UserFormModeTypes.PREVIEW_PROPS
            }
          />
        );
      case "thums":
        return (
          <div>
            <ThumbSwitch
              stateOverride={localValue}
              onToggle={onChangeLocalValue}
              isDisabled={
                mode === UserFormModeTypes.BUILD ||
                mode === UserFormModeTypes.PREVIEW ||
                mode === UserFormModeTypes.PREVIEW_PROPS
              }
            />
          </div>
        );

      default:
        return null;
    }
  };

  useEffect(() => {
    onChange(localValue);
  }, [localValue]);

  useEffect(() => {
    const token = formEventEmitter.addListener(
      FORM_EVENTS.SAVE_AND_CONTINUE,
      () => {
        if (localValue === true || localValue === false) {
          setError(false);
          onChange(localValue);
        } else {
          setError(true);
        }
      }
    );
    return () => {
      token.remove();
    };
  }, [localValue, onChange]);

  useEffect(() => {
    if (error) {
      if (localValue === true || localValue === false) {
        setError(false);
      } else {
        setError(true);
      }
    }
  }, [error, localValue]);

  return (
    <div className="flex flex-col">
      {inSummary && content.properties.toggle_style === "text" ? (
        <div className="flex flex-col gap-2">
          <ComponentLabel className="text-sm font-semibold cursor-auto">
            {content.properties.title}
          </ComponentLabel>
          <div className={style.yesOrNoComponentParent__switchComponent}>
            {renderSwitchType(content.properties.toggle_style)}
          </div>
        </div>
      ) : (
        <div className={style.yesOrNoComponentParent}>
          <div className="flex gap-2">
            <p className={style.yesOrNoComponentParent__question}>
              {content.properties.title}{" "}
              {content.properties.is_mandatory && !inSummary ? "*" : ""}
            </p>
            {include_in_widget && mode === "BUILD" && (
              <div className="text-neutrals-tertiary flex gap-2">
                <SvgButton svgPath={"/assets/CWF/widget.svg"} />
                <BodyText className="text-neutrals-tertiary">Widget</BodyText>
              </div>
            )}
          </div>
          <div className={style.yesOrNoComponentParent__switchComponent}>
            {renderSwitchType(content.properties.toggle_style)}
          </div>
        </div>
      )}
      {error && content.properties.is_mandatory && (
        <p className="text-red-500 mt-2">This is required</p>
      )}
    </div>
  );
};

export default YesOrNo;
