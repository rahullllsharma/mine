import type { PropsWithClassName } from "@/types/Generic";
import type { IconName } from "@urbint/silica";
import cx from "classnames";
import { Icon } from "@urbint/silica";

type TabItemProps = PropsWithClassName<{
  value: string;
  icon?: IconName;
  type?: "regular" | "menu";
}>;

export default function TabItem({
  value,
  icon,
  type = "regular",
  className,
}: TabItemProps): JSX.Element {
  return (
    <div
      className={cx(
        "flex items-center",
        { ["px-2.5 py-3"]: type === "regular" },
        { ["flex-col h-full gap-0 pt-2"]: type === "menu" },
        className
      )}
    >
      {icon && (
        <Icon
          name={icon}
          className={cx({
            ["text-xl mr-1 text-neutral-shade-75"]: type === "regular",
            ["text-2xl w-7 h-7 leading-7"]: type === "menu",
          })}
        />
      )}
      <span
        className={cx({
          ["text-base mx-1 truncate"]: type === "regular",
          ["text-sm truncate"]: type === "menu",
        })}
      >
        {value}
      </span>
    </div>
  );
}
