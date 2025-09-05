import type { CalendarButtonProps } from "../CalendarButton";
import { Icon } from "@urbint/silica";
import CalendarButton from "../CalendarButton";

export type CalendarNavButtonProps = CalendarButtonProps & {
  icon: "chevron_big_left" | "chevron_big_right";
};

export default function CalendarNavButton({
  icon,
  ...tailProps
}: CalendarNavButtonProps): JSX.Element {
  const label = icon === "chevron_big_left" ? "Last week" : "Next week";

  return (
    <CalendarButton {...tailProps}>
      <Icon name={icon} className="text-xl leading-5 text-neutral-shade-75" />
      <span className="mt-1 text-xs font-base text-neutral-shade-100">
        {label}
      </span>
    </CalendarButton>
  );
}
