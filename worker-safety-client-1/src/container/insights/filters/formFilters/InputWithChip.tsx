import type { ForwardedRef, HTMLProps } from "react";
import type { MultiOption } from "src/components/templatesComponents/customisedForm.types";
import type { IconName } from "@urbint/silica";
import { forwardRef } from "react";
import cx from "classnames";
import { Icon } from "@urbint/silica";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";

export type InputWithChipsProps = HTMLProps<HTMLInputElement> & {
  chips?: MultiOption[];
  onRemoveChip?: (id: string) => void;
  icon?: string;
  placeholder?: string;
};

const containerBaseStyles = `
  relative flex flex-row flex-wrap items-center w-full text-base
  border border-neutral-shade-26 rounded-md bg-neutral-light-100
  focus-within:ring-1 focus-within:ring-brand-gray-60 px-2
`;

const chipBaseStyles = `
  flex items-center cursor-pointer hover:shadow-5
  border border-brand-urbint-30 bg-brand-urbint-10
  text-neutral-shade-100 text-sm px-2 py-1 rounded-md
  mr-1 my-1
`;

const RedPlaceholderStyle = () => (
  <style
    dangerouslySetInnerHTML={{
      __html: `
      .grey-placeholder::placeholder {
        color: grey !important;
      }
    `,
    }}
  />
);

// eslint-disable-next-line react/display-name
const InputWithChips = forwardRef<HTMLInputElement, InputWithChipsProps>(
  (
    {
      chips = [],
      onRemoveChip,
      icon,
      className,
      placeholder = "Search for users",
      readOnly,
      disabled,
      ...props
    },
    ref: ForwardedRef<HTMLInputElement>
  ) => {
    return (
      <>
        <RedPlaceholderStyle />
        <div
          className={cx(containerBaseStyles, {
            "bg-transparent border-none": readOnly,
          })}
        >
          {icon && !readOnly && chips.length === 0 && (
            <Icon
              name={icon as IconName}
              className={cx(
                "text-xl ml-1 mt-1 pointer-events-none w-5 h-9 text-neutral-shade-58"
              )}
            />
          )}

          {chips.map(chip => (
            <div key={chip.id} className={chipBaseStyles}>
              <span className="text-sm px-[-1rem]">{chip.name}</span>
              <ButtonIcon
                iconName="off_outline_close"
                className="w-4 h-4 text-neutral-shade-38 hover:text-neutral-shade-58 flex items-center"
                onClick={() => onRemoveChip?.(chip.id)}
              />
            </div>
          ))}

          <input
            ref={ref}
            placeholder={chips.length === 0 ? placeholder : ""}
            disabled={disabled || readOnly}
            className={cx(
              "focus:outline-none flex-grow ml-1 min-w-[1rem] px-1 py-2 text-sx grey-placeholder",
              className
            )}
            {...props}
          />
        </div>
      </>
    );
  }
);

export default InputWithChips;
