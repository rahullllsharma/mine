import { Listbox } from "@headlessui/react";
import type { IconName } from "@urbint/silica";
import { Icon } from "@urbint/silica";
import cx from "classnames";
import type { HTMLAttributes, RefCallback } from "react";
import { Fragment, useEffect, useState } from "react";

// TODO: extract proper classNames(bag) argument for the ListboxOptionArgs type
// But we need to infer the proper generic for the classNames to return the Function, for now, just copied & pasted.
// type ListboxOptionArgs = Parameters<typeof Listbox.Option>[0];
type ListboxOptionArgs = {
  active: boolean;
  selected: boolean;
  disabled: boolean;
};

// eslint-disable-next-line @typescript-eslint/ban-types
export type SelectOption<T = {}> = T & {
  id: number | string;
  name: string;
  status?: string;
  isDisabled?: boolean;
  tooltip?: SelectOptionTooltip;
  subOptions?: Readonly<SelectOption<T>[]>;
  icon?: IconName;
};
export type Status =
  | "default"
  | "current"
  | "saved"
  | "saved_current"
  | "error";

export type SelectOptionTooltip = {
  icon: IconName;
  text: string;
};

// eslint-disable-next-line @typescript-eslint/ban-types
type RenderOptionFnArgs<T = {}> = {
  listboxOptionProps: ListboxOptionArgs;
  option: SelectOption<T>;
};

// eslint-disable-next-line @typescript-eslint/ban-types
export type RenderOptionFn<T = {}> = (
  renderOptionArgs: RenderOptionFnArgs<T>
) => JSX.IntrinsicElements["li"];

type SelectButtonSize = "default" | "small";

// eslint-disable-next-line @typescript-eslint/ban-types
export type SelectProps<T = {}> = Pick<
  HTMLAttributes<HTMLElement>,
  "className"
> & {
  options: Readonly<SelectOption<T>[]>;
  defaultOption?: SelectOption<T>;
  isInvalid?: boolean;
  buttonRef?: RefCallback<HTMLButtonElement>;
  onSelect: (option: SelectOption<T>) => void;
  optionsClassNames?: string;
  allowMultilineBox?: boolean;
  /**
   * Since the Listbox.Options is always a <ul>, we must ALWAYS return <li>.
   * If the Listbox.Options changes, then we can expand this
   */
  renderOptionFn: RenderOptionFn<T>;
  size?: SelectButtonSize;
  placeholder?: string;
  renderSelectedValue?: (
    option: SelectOption<T> | undefined
  ) => React.ReactNode;
};

const getDisplayText = (
  selectedOption: SelectOption | undefined,
  isDisabled: boolean,
  placeholder: string
): string => {
  if (!!selectedOption) {
    return selectedOption.name;
  }

  return isDisabled ? "No options available" : placeholder;
};

const getButtonStyles = (
  isOpen: boolean,
  size: SelectButtonSize,
  isInvalid: boolean,
  isDisabled: boolean,
  defaultOption?: SelectOption
): string => {
  const staticStyles =
    "w-full px-2 py-0.5 flex items-center justify-between bg-white text-base rounded border border-solid outline-none focus-within:ring-1 focus-within:ring-brand-gray-60";

  const styles = {
    ["h-7"]: size === "small",
    ["border-system-error-40 focus-within:ring-system-error-40"]: isInvalid,
    ["border-brand-gray-60"]: isOpen && !isInvalid,
    ["border-neutral-shade-26"]: !isOpen && !isInvalid,
    ["text-neutral-shade-58"]: !defaultOption,
    ["bg-neutral-shade-7 cursor-not-allowed"]: isDisabled,
  };

  return cx(staticStyles, styles);
};

/**
 * The Select base, should be used as an abstraction for other Select components.
 * @private
 */
export function Select<T>({
  options,
  defaultOption,
  isInvalid = false,
  buttonRef,
  className,
  onSelect,
  renderOptionFn = ({ option: { name } }) => <li>{name}</li>,
  optionsClassNames,
  size = "default",
  placeholder = "Select an option",
  allowMultilineBox = false,
  renderSelectedValue,
}: SelectProps<T>): JSX.Element {
  const isDisabled = options.length === 0;

  return (
    <Listbox
      value={defaultOption}
      onChange={onSelect}
      disabled={isDisabled}
      // TODO: once this is on Silica, we need a proper selector
      data-testid="select"
    >
      {({ open }) => (
        <div className={cx("relative text-neutral-shade-100", className)}>
          <Listbox.Button
            className={getButtonStyles(
              open,
              size,
              isInvalid,
              isDisabled,
              defaultOption
            )}
            ref={buttonRef}
          >
            {renderSelectedValue ? (
              renderSelectedValue(defaultOption)
            ) : (
              <span
                className={
                  allowMultilineBox
                    ? "line-clamp-2 text-left flex items-center"
                    : "truncate flex items-center"
                }
              >
                {defaultOption?.icon && (
                  <Icon name={defaultOption.icon} className="mr-2" />
                )}
                {getDisplayText(defaultOption, isDisabled, placeholder)}
              </span>
            )}
            <Icon
              name="chevron_down"
              className="text-neutral-shade-58 text-xl"
            />
          </Listbox.Button>
          <Listbox.Options
            className={cx(
              "absolute z-10 w-full mt-2 max-h-60 overflow-auto shadow-20 rounded bg-white outline-none",
              optionsClassNames
            )}
          >
            {options.map(option => (
              <Fragment key={option.id}>
                <Listbox.Option
                  value={option}
                  as={Fragment}
                  disabled={option.isDisabled}
                >
                  {listboxOptionProps =>
                    renderOptionFn({ listboxOptionProps, option })
                  }
                </Listbox.Option>
                {(option.subOptions || []).map(subOption => (
                  <Listbox.Option
                    key={subOption.id}
                    value={subOption}
                    as={Fragment}
                    disabled={subOption.isDisabled}
                  >
                    {listboxOptionProps =>
                      renderOptionFn({ listboxOptionProps, option: subOption })
                    }
                  </Listbox.Option>
                ))}
              </Fragment>
            ))}
          </Listbox.Options>
        </div>
      )}
    </Listbox>
  );
}

/**
 * The Select component but with internal state. Mostly for compatibility with current components that
 * depend on the Select internal state but we should review and (probably) remove this version
 *
 * @deprecated
 * @private
 */
export default function StatefulSelect<T>(props: SelectProps<T>): JSX.Element {
  const getDefaultOption = () =>
    props.options.find(option => option.id === props?.defaultOption?.id);

  const [selectedOption, setSelectedOption] = useState(() =>
    getDefaultOption()
  );

  useEffect(() => {
    // TODO: Extract .find method to an auxiliary function to be reused
    setSelectedOption(getDefaultOption());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [props.defaultOption]);

  const onSelect: SelectProps<T>["onSelect"] = item => {
    setSelectedOption(item);
    props?.onSelect(item);
  };

  return (
    <Select {...props} onSelect={onSelect} defaultOption={selectedOption} />
  );
}
