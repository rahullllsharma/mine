import type { PropsWithChildren } from "react";
import type * as t from "io-ts";
import type { FormField } from "@/utils/formField";
import type { Option } from "fp-ts/lib/Option";
import type { IconName } from "@urbint/silica";
import type { UserFormMode } from "@/components/templatesComponents/customisedForm.types";
import { BodyText, Icon } from "@urbint/silica";

import * as O from "fp-ts/lib/Option";
import { isLeft } from "fp-ts/lib/Either";
import cx from "classnames";

import SvgButton from "@/components/templatesComponents/ButtonComponents/SvgButton/SvgButton";
import { ErrorMessage } from "../../ErrorMessage";

export type CommonInputLayoutProps<V> = {
  id?: string;
  className?: string;
  label?: string;
  disabled?: boolean;
  htmlFor?: string;
  field: FormField<t.Errors, string, V>;
  includeInWidget?: boolean;
  mode?: UserFormMode;
};

type InputLayoutProps<V> = CommonInputLayoutProps<V> & {
  icon: Option<IconName>;
  error?: boolean;
  errorMessage?: string;
};

const containerStaticStyles = `relative flex w-full items-center text-base font-normal text-neutral-shade-100 rounded-md border border-solid`;

function InputLayout<V>(props: PropsWithChildren<InputLayoutProps<V>>) {
  const {
    id,
    children,
    className,
    disabled,
    label,
    field,
    icon,
    error,
    errorMessage,
    includeInWidget,
    mode,
  } = props;
  const { val, dirty } = field;
  const hasError = (dirty && isLeft(val)) || error;

  return (
    <div id={id} className={className}>
      {label && (
        <div className="flex gap-2 mb-2">
          <label className="block text-tiny md:text-sm text-neutral-shade-75 font-semibold mb-1 leading-normal">
            {label}
          </label>
          {includeInWidget && mode === "BUILD" && (
            <div className="text-neutrals-tertiary flex gap-2">
              <SvgButton svgPath={"/assets/CWF/widget.svg"} />
              <BodyText className="text-neutrals-tertiary">Widget</BodyText>
            </div>
          )}
        </div>
      )}

      <div
        className={cx(
          containerStaticStyles,
          hasError
            ? "border-system-error-40 focus-within:ring-0"
            : "border-neutral-shade-26 focus-within:ring-1 focus-within:ring-brand-gray-60"
        )}
      >
        {O.isSome(icon) && (
          <Icon
            name={icon.value}
            className={cx(
              "ml-2 pointer-events-none w-6 h-6 text-xl leading-none bg-white",
              {
                ["opacity-38"]: disabled,
                ["text-neutral-shade-58"]: !disabled,
              }
            )}
          />
        )}
        {children}
      </div>
      {hasError && errorMessage ? (
        <p className="text-red-500 mt-2">{errorMessage}</p>
      ) : (
        hasError && <ErrorMessage field={field} />
      )}
    </div>
  );
}

export { InputLayout };
