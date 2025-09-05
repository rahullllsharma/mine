import type { IconName } from "@urbint/silica";
import type { PropsWithClassName } from "@/types/Generic";
import type { TooltipProps } from "../../tooltip/Tooltip";
import cx from "classnames";
import { Icon } from "@urbint/silica";
import Popover from "../Popover";
import Tooltip from "../../tooltip/Tooltip";

export type PopoverIconProps = PropsWithClassName<{
  iconName: IconName;
  iconClass?: string;
  tooltipProps?: Omit<TooltipProps, "children>">;
}>;

export default function PopoverIcon({
  iconName,
  iconClass,
  tooltipProps,
  className,
  children,
}: PopoverIconProps): JSX.Element {
  const icon: JSX.Element = (
    <Icon name={iconName} className={cx("text-xl", iconClass)} />
  );
  const trigger: JSX.Element = (
    <button className="flex">
      {tooltipProps ? <Tooltip {...tooltipProps}>{icon}</Tooltip> : icon}
    </button>
  );

  return (
    <Popover triggerComponent={trigger} className={className}>
      {children}
    </Popover>
  );
}
