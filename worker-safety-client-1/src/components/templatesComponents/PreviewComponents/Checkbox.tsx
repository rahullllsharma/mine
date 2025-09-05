import type { CheckboxPreviewProps } from "../customisedForm.types";
import React, { useState, useEffect } from "react";
import { BodyText, CaptionText } from "@urbint/silica";
import {
  FORM_EVENTS,
  formEventEmitter,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import Checkbox from "@/components/shared/checkbox/Checkbox";
import Link from "@/components/shared/link/Link";
import { disabledField } from "../customisedForm.utils";
import SvgButton from "../ButtonComponents/SvgButton/SvgButton";

const CheckboxPreview: React.FC<CheckboxPreviewProps> = ({
  content,
  onChange,
  mode,
  inSummary,
}) => {
  const {
    title,
    is_mandatory,
    user_value = [],
    options = [],
    include_in_widget,
  } = content.properties;
  const url = options.length > 0 ? options[0].url : "";
  const url_display_text =
    options.length > 0 ? options[0].url_display_text : "";
  const [localValue, setLocalValue] = useState<string[]>(user_value || []);
  const [error, setError] = useState(false);

  const isChecked = localValue.includes("1");

  useEffect(() => {
    onChange(localValue);
  }, [localValue]);

  useEffect(() => {
    const token = formEventEmitter.addListener(
      FORM_EVENTS.SAVE_AND_CONTINUE,
      () => {
        if (is_mandatory && !isChecked) {
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
  }, [localValue, is_mandatory, isChecked, onChange]);

  useEffect(() => {
    if (error) {
      if (localValue.includes("1")) {
        setError(false);
      } else {
        setError(true);
      }
    }
  }, [error, localValue]);

  const handleCheckboxChange = () => {
    setLocalValue(prev => (prev.includes("1") ? [] : ["1"]));
  };

  return (
    <div className="flex flex-col gap-2" id={content.id}>
      <div className="flex items-center gap-2">
        {!inSummary && (
          <Checkbox
            checked={isChecked}
            onChange={handleCheckboxChange}
            disabled={disabledField(mode)}
            hasError={error}
          />
        )}

        <div className="flex gap-2">
          <BodyText className="text-base">
            {title}
            {is_mandatory && !inSummary && (
              <span className="text-black ml-1">*</span>
            )}
          </BodyText>
          {include_in_widget && mode === "BUILD" && (
            <div className="text-neutrals-tertiary flex gap-2">
              <SvgButton svgPath={"/assets/CWF/widget.svg"} />
              <BodyText className="text-neutrals-tertiary">Widget</BodyText>
            </div>
          )}
        </div>
      </div>
      {error && (
        <CaptionText className="text-red-500 text-sm mt-1 ml-7 cursor-auto">
          This is required
        </CaptionText>
      )}
      {url && url_display_text && (
        <Link
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          label={url_display_text}
          iconRight="external_link"
          className={`text-base mt-1 ${
            inSummary ? "font-semibold" : "font-normal ml-7"
          }`}
          style={{
            wordBreak: "break-word",
          }}
        />
      )}
    </div>
  );
};

export default CheckboxPreview;
