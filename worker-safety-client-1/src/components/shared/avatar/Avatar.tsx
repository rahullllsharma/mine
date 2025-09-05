import type { PropsWithClassName } from "@/types/Generic";
import cx from "classnames";

export type AvatarProps = PropsWithClassName<{
  name: string;
}>;

export default function Avatar({
  name,
  className,
  children,
}: AvatarProps): JSX.Element {
  return (
    <div
      className={cx(
        "w-7 h-7 rounded-full flex items-center justify-center",
        className
      )}
      role="img"
      aria-label={name}
    >
      {children}
    </div>
  );
}
