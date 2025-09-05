import type {
  ControlProps,
  OptionProps,
  GroupBase,
  DropdownIndicatorProps,
  ClearIndicatorProps,
  IndicatorSeparatorProps,
  StylesConfig,
  MultiValueGenericProps,
  MultiValueRemoveProps,
  Props,
} from "react-select";
import type { FocusEventHandler, RefCallback } from "react";
import type { SelectOptionTooltip } from "../select/Select";
import type { IconName } from "@urbint/silica";
import type { PropsWithClassName } from "@/types/Generic";
import { Icon } from "@urbint/silica";
import cx from "classnames";
import Select, { components } from "react-select";
import { hexToRgba } from "@/components/templatesComponents/customisedForm.utils"; 

interface CustomSelectProps<
  Option,
  IsMulti extends boolean,
  Group extends GroupBase<Option>
> extends Props<Option, IsMulti, Group> {
  customColor?: HexColor;
  isInvalid?: boolean;
  size?: SelectControlSize;
  buttonRef?: RefCallback<HTMLDivElement>;
  icon?: IconName;
}

// This object allows us to take full control over the styles in individual components. We'll override completely the ones we want to fully customize
// In case we need to make a very(!) minor change (like suppressing a margin :p), we can do it here
const customStyles: StylesConfig<
  InputSelectOption,
  true,
  GroupBase<InputSelectOption>
> = {
  option: () => ({}),
  control: () => ({}),
  menu: () => ({}),
  dropdownIndicator: base => ({ ...base, padding: "0px 8px" }),
  clearIndicator: base => ({ ...base, padding: "0px 8px" }),
  multiValue: () => ({}),
  singleValue: base => ({ ...base, margin: 0 }),
  input: base => ({ ...base, margin: 0 }),
  placeholder: base => ({
    ...base,
    margin: 0,
    whiteSpace: "nowrap",
    overflow: "hidden",
    textOverflow: "ellipsis",
  }),
  valueContainer: base => ({
    ...base,
    padding: "2px 0 0 0",
    gap: "4px",
  }),
  multiValueLabel: base => ({
    ...base,
    whiteSpace: "normal",
    padding: "4px 0 4px 6px",
  }),
};

const staticStyles =
  "w-full pr-2 py-0.5 flex items-center justify-between bg-white text-base rounded border border-solid outline-none focus-within:ring-1 focus-within:ring-brand-gray-60 cursor-pointer";

export type InputSelectOption = {
  id: string;
  name: string;
  isDisabled?: boolean;
  tooltip?: SelectOptionTooltip;
  customColor?: HexColor;
  closeMenuOnSelect?: boolean;
};

export type IngestDataItemsColumn = {
  attribute: string;
  name: string;
  requiredOnIngest: boolean;
  ignoreOnIngest: boolean;
};

export type IngestDataSelectOptionType = InputSelectOption & {
  description: string;
  columns: IngestDataItemsColumn[];
};

type SelectControlSize = "regular" | "sm";

export type HexColor = `#${string}`;

export type InputSelectProps<T = InputSelectOption | InputSelectOption[]> =
  PropsWithClassName<{
    placeholder?: string;
    options: Readonly<InputSelectOption[]>;
    isInvalid?: boolean;
    size?: SelectControlSize;
    defaultOption?: T;
    value?: T | null;
    isClearable?: boolean;
    isSearchable?: boolean;
    isMulti?: true;
    icon?: IconName;
    buttonRef?: RefCallback<HTMLDivElement>;
    onSelect: (option: Readonly<T>) => void;
    onBlur?: FocusEventHandler<HTMLInputElement>;
    disableSelect?: boolean;
    customColor?: HexColor;
    onInputChange?: (newValue: string) => void;
    closeMenuOnSelect?: boolean;
  }>;

// Defining components individually and outside the scope of the select, as recommended (https://react-select.com/components#defining-components)

// Customizing control component, (wraps the value container and the indicator container)
const Control = ({
  children,
  ...props
}: ControlProps<InputSelectOption, true, GroupBase<InputSelectOption>>) => {
  const customProps = props.selectProps as CustomSelectProps<
    InputSelectOption,
    true,
    GroupBase<InputSelectOption>
  >;

  const { isInvalid, menuIsOpen, isDisabled, size, buttonRef, icon } =
    customProps;

  const innerProps = { ...props.innerProps, role: "button" };
  const controlProps = {
    ...props,
    className: cx(staticStyles, {
      ["h-7"]: size === "sm",
      ["border-system-error-40 focus-within:ring-system-error-40"]: isInvalid,
      ["border-neutral-shade-26"]: !menuIsOpen && !isInvalid,
      ["text-neutral-shade-58"]: !props.hasValue,
      ["bg-neutral-shade-7 cursor-not-allowed"]: isDisabled,
      ["pl-3"]: !icon,
    }),
    innerProps: innerProps,
    ...(buttonRef ? { innerRef: buttonRef } : {}),
  };

  return (
    <components.Control {...controlProps}>
      {icon && (
        <div
          className={cx(
            "ml-2 mr-1 pointer-events-none w-6 h-6 text-xl leading-none bg-white",
            {
              ["opacity-38"]: isDisabled,
              ["text-neutral-shade-58"]: !isDisabled,
            }
          )}
        >
          <Icon name={icon} />
        </div>
      )}
      {children}
    </components.Control>
  );
};

// Customizing Menu component (wraps the options)

// Customizing options individually
const Option = (
  props: OptionProps<InputSelectOption, true, GroupBase<InputSelectOption>>
) => {
  const { isSelected, isFocused, children } = props;

  // to overcome react-select limitations for the unit tests
  const innerProps = { ...props.innerProps, role: "option" };
  return (
    <components.Option
      {...props}
      innerProps={innerProps}
      className={cx("flex items-center p-3 text-base cursor-pointer", {
        ["bg-brand-gray-10"]: isSelected || isFocused,
        ["text-brand-urbint-50 font-medium"]: isSelected,
      })}
    >
      {children}
    </components.Option>
  );
};

// Customizing dropdown indicator so we can use our own icon
const DropdownIndicator = (
  props: DropdownIndicatorProps<
    InputSelectOption,
    true,
    GroupBase<InputSelectOption>
  >
) => {
  return (
    <components.DropdownIndicator {...props}>
      <Icon name="chevron_down" className="text-neutral-shade-58 text-xl" />
    </components.DropdownIndicator>
  );
};

// Customizing clear indicator so we can use our own icon
const ClearIndicator = (
  props: ClearIndicatorProps<
    InputSelectOption,
    true,
    GroupBase<InputSelectOption>
  >
) => {
  return (
    <components.ClearIndicator {...props}>
      <Icon name="close_small" className="text-neutral-shade-58 text-xl" />
    </components.ClearIndicator>
  );
};

// Customizing separator indicator in order to just show it when we have values in the select
const IndicatorSeparator = (
  props: IndicatorSeparatorProps<
    InputSelectOption,
    true,
    GroupBase<InputSelectOption>
  >
) => {
  return props.hasValue ? <components.IndicatorSeparator {...props} /> : null;
};

// Customizing the Option chip container, in multi value selection

const MultiValueContainer = (
  props: MultiValueGenericProps<
    InputSelectOption,
    true,
    GroupBase<InputSelectOption>
  >
) => {
  // Use type assertion to tell TypeScript that selectProps has our custom properties
  const customProps = props.selectProps as CustomSelectProps<
    InputSelectOption,
    true,
    GroupBase<InputSelectOption>
  >;

  const { customColor } = customProps;

  return (
    <components.MultiValueContainer {...props}>
      <div
        className="border-brand-urbint-30 bg-brand-urbint-10 flex border rounded-md text-neutral-shade-100 hover:bg-white hover:shadow-5 flex-nowrap cursor-pointer"
        style={{
          ...(customColor
            ? {
                borderColor: customColor,
                backgroundColor: hexToRgba(customColor, 0.3),
              }
            : {}),
          transition: "background-color 0.3s ease",
        }}
      >
        {props.children}
      </div>
    </components.MultiValueContainer>
  );
};

// Adding our own icon to the Option chip, to remove value from selection
const MultiValueRemove = (
  props: MultiValueRemoveProps<
    InputSelectOption,
    true,
    GroupBase<InputSelectOption>
  >
) => {
  const className =
    "text-neutral-shade-38 hover:text-neutral-shade-58 flex items-center px-1";
  const innerProps = { ...props.innerProps, className };
  return (
    <components.MultiValueRemove {...props} innerProps={innerProps}>
      <Icon name="off_outline_close" />
    </components.MultiValueRemove>
  );
};

export default function InputSelect({
  placeholder,
  className,
  options,
  defaultOption,
  value,
  buttonRef,
  isInvalid = false,
  size = "regular",
  onSelect,
  onBlur,
  isSearchable = false,
  isClearable = false,
  isMulti,
  icon,
  disableSelect,
  customColor,
  closeMenuOnSelect,
}: InputSelectProps): JSX.Element {
  // passing these props to the child components, so they can be accessed as selectProps
  const customProps = { isInvalid, size, buttonRef, icon, onBlur, customColor };

  const noOptionsMessage = "No options available";
  const isDisabled = options?.length === 0;
  const placeholderMessage = isDisabled ? noOptionsMessage : placeholder;

  const separator = isClearable ? IndicatorSeparator : undefined;

  return (
    <Select
      maxMenuHeight={400}
      getOptionValue={option => option.id}
      getOptionLabel={option => option.name}
      options={options}
      placeholder={placeholderMessage}
      isSearchable={isSearchable}
      styles={{
        ...customStyles,
        menu: base => ({
          ...base,
          zIndex: 1050,
          maxHeight: "400px",
          overflowY: "auto",
        }),
      }}
      defaultValue={defaultOption}
      value={value}
      className={className}
      isMulti={isMulti}
      isClearable={isClearable}
      closeMenuOnSelect={closeMenuOnSelect}
      components={{
        Option,
        Control,
        Menu: props => (
          <components.Menu
            {...props}
            className="absolute z-10 w-full mt-2 mb-10 shadow-20 rounded bg-white outline-none"
          />
        ),
        DropdownIndicator,
        IndicatorSeparator: separator,
        ClearIndicator,
        MultiValueContainer,
        MultiValueRemove,
      }}
      onChange={onSelect}
      isDisabled={isDisabled || disableSelect}
      noOptionsMessage={() => noOptionsMessage}
      menuPlacement="auto"
      {...customProps}
    />
  );
}
