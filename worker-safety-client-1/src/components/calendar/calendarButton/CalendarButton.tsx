import type { PropsWithClassName } from "@/types/Generic";
import cx from "classnames";

export type CalendarButtonProps = PropsWithClassName<{
  isActive?: boolean;
  isToday?: boolean;
  isDisabled?: boolean;
  onClick: () => void;
}>;

const disabledStyles = "disabled:opacity-30 disabled:cursor-not-allowed";

export default function CalendarButton({
  isActive,
  isToday,
  isDisabled,
  onClick,
  children,
  className,
}: CalendarButtonProps): JSX.Element {
  const isDefaultBorder = !isToday && !isActive;
  const borderStyles = cx("border rounded-xl border rounded-xl", {
    ["border-brand-gray-40"]: isDefaultBorder,
    ["border-4"]: isActive,
    ["border-brand-urbint-40"]: isToday,
    ["border-4 border-brand-gray-70"]: isActive && !isToday,
  });

  const attributes: { [key: string]: boolean } = {};
  if (isToday) {
    attributes["data-is-today"] = true;
  }
  if (isActive) {
    attributes["data-is-selected"] = true;
  }

  return (
    <button
      disabled={isDisabled}
      className={cx(
        "h-20 w-20 flex flex-col items-center justify-center",
        className,
        disabledStyles,
        borderStyles
      )}
      onClick={onClick}
      {...attributes}
    >
      {children}
    </button>
  );
}
