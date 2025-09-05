import type { SelectProps, SelectOption, RenderOptionFn } from "../Select";
import { Icon } from "@urbint/silica";
import cx from "classnames";
import Tooltip from "../../tooltip/Tooltip";
import Select from "../Select";

export type SelectPrimaryProps = Omit<SelectProps, "renderOptionFn">;
export type SelectPrimaryOption = SelectOption;

export const defaultRenderOptionFn: RenderOptionFn = ({
  option: { name, isDisabled, tooltip },
  listboxOptionProps: { active, selected },
}) => (
  <li
    className={cx(
      "flex items-center h-10 px-3 text-base cursor-pointer truncate",
      {
        ["bg-brand-gray-10"]: (active || selected) && !isDisabled,
        ["text-brand-urbint-50 font-medium"]: selected,
        ["text-neutral-shade-38 cursor-not-allowed"]: isDisabled,
        ["justify-between"]: tooltip,
      }
    )}
  >
    <span className="truncate">{name}</span>
    {tooltip && (
      <Tooltip title={tooltip.text} position="bottom" className="max-w-xs">
        <Icon name={tooltip.icon} className="text-xl text-neutral-shade-75" />
      </Tooltip>
    )}
  </li>
);

export default function SelectPrimary(props: SelectPrimaryProps): JSX.Element {
  return (
    <Select
      {...props}
      renderOptionFn={defaultRenderOptionFn}
      optionsClassNames="py-2"
    />
  );
}
