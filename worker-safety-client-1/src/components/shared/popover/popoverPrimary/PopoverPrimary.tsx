import type { IconName } from "@urbint/silica";
import type { PropsWithClassName } from "@/types/Generic";
import cx from "classnames";
import Popover from "../Popover";
import ButtonPrimary from "../../button/primary/ButtonPrimary";

export type PopoverPrimaryProps = PropsWithClassName<{
  label: string;
  iconStart?: IconName;
  iconEnd?: IconName;
  buttonClass?: string;
}>;

export default function PopoverPrimary({
  label,
  iconStart,
  iconEnd,
  buttonClass,
  className,
  children,
}: PopoverPrimaryProps): JSX.Element {
  const trigger: JSX.Element = (
    <ButtonPrimary
      label={label}
      iconStart={iconStart}
      iconEnd={iconEnd}
      className={cx(buttonClass)}
    />
  );

  return (
    <Popover triggerComponent={trigger} className={className}>
      {children}
    </Popover>
  );
}
