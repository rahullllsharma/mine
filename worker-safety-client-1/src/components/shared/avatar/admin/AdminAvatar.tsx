import type { AvatarProps } from "../Avatar";
import cx from "classnames";
import { Icon } from "@urbint/silica";
import Avatar from "../Avatar";

type AdminAvatarProps = Pick<AvatarProps, "className">;

export default function AdminAvatar({
  className,
}: AdminAvatarProps): JSX.Element {
  return (
    <Avatar name="Urbint" className={cx("bg-transparent", className)}>
      <Icon name="urbint" className="text-2xl text-brand-urbint-50" />
    </Avatar>
  );
}
