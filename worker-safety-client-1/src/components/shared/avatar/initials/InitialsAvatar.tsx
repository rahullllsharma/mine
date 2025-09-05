import type { AvatarProps } from "../Avatar";
import cx from "classnames";
import { getUserInitials } from "../utils";
import Avatar from "../Avatar";

export type InitialsAvatarProps = AvatarProps;

export default function InitialsAvatar({
  name,
  className,
}: InitialsAvatarProps): JSX.Element {
  const initials = getUserInitials(name);

  return (
    <Avatar name={initials} className={cx("bg-data-blue-40", className)}>
      <span className="text-sm font-semibold uppercase text-neutral-light-100">
        {initials}
      </span>
    </Avatar>
  );
}
