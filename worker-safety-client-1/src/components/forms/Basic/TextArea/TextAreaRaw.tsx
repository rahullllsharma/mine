import type { IconName } from "@urbint/silica";
import type { UserFormMode } from "@/components/templatesComponents/customisedForm.types";
import { BodyText, CaptionText, Icon } from "@urbint/silica";
import cx from "classnames";
import { useRef } from "react";
import SvgButton from "@/components/templatesComponents/ButtonComponents/SvgButton/SvgButton";

export type InputRawProps = {
  id?: string;
  type?: string;
  label?: string;
  sublabel?: string;
  icon?: IconName;
  clearIcon?: boolean;
  mode?: UserFormMode;
  includeInWidget?: boolean;
  placeholder?: string;
  disabled?: boolean;
  hasError?: boolean;
  value?: string;
  onChange: (value: string) => void;
  regex?: RegExp;
  onBlur?: (value: string) => void;
};

export function TextAreaRaw(props: InputRawProps): JSX.Element {
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const handleInputChange = (value: string) => {
    // If a regex is provided, use it to filter input
    const filteredValue = props.regex ? value.replace(props.regex, "") : value;
    props.onChange(filteredValue);
  };
  return (
    <div className="w-full" id={props.id}>
      {props.label && (
        <div className="flex gap-2 mb-1">
          <label className="block text-tiny md:text-sm text-neutral-shade-75 font-semibold mb-1 leading-normal">
            {props.label}
          </label>
          {props.includeInWidget && props.mode === "BUILD" && (
            <div className="text-neutrals-tertiary flex gap-2">
              <SvgButton svgPath={"/assets/CWF/widget.svg"} />
              <BodyText className="text-neutrals-tertiary">Widget</BodyText>
            </div>
          )}
        </div>
      )}
      {props.sublabel && (
        <CaptionText className="text-neutral-shade-75 md:text-sm">
          {props.sublabel}
        </CaptionText>
      )}
      <div
        className={cx(
          "relative flex w-full items-center text-base font-normal text-neutral-shade-100 border border-solid rounded-md focus-within:ring-1 focus-within:ring-brand-gray-60 bg-neutral-light-100",
          props.hasError
            ? "border-system-error-40 focus-within:ring-0"
            : "border-neutral-shade-26 focus-within:ring-1 focus-within:ring-brand-gray-60"
        )}
      >
        {props.icon && (
          <Icon
            name={props.icon}
            className={cx(
              "ml-2 pointer-events-none w-6 h-6 text-xl leading-none bg-white",
              {
                ["opacity-38"]: props.disabled,
                ["text-neutral-shade-58"]: !props.disabled,
              }
            )}
          />
        )}
        <textarea
          rows={4}
          disabled={props.disabled}
          value={props.value}
          ref={inputRef}
          placeholder={props.placeholder}
          className={
            "p-2 flex-auto rounded-md appearance-none focus:outline-none disabled:bg-neutral-light-77 read-only:cursor-default disabled:cursor-not-allowed disabled:opacity-38 min-w-0"
          }
          onChange={e => handleInputChange(e.target.value)}
          onBlur={e => props.onBlur && props.onBlur(e.target.value)}
        />
        {props.clearIcon && inputRef?.current?.value !== "" && (
          <Icon
            name={"close_small"}
            className={cx(
              "ml-2 cursor-pointer w-6 h-6 text-xl leading-none bg-white ",
              {
                ["opacity-38"]: props.disabled,
                ["text-neutral-shade-58"]: !props.disabled,
              }
            )}
            onClick={() => {
              inputRef.current && (inputRef.current.value = "");
            }}
          />
        )}
      </div>
    </div>
  );
}
