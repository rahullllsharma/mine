import { Icon } from "@urbint/silica";
import cx from "classnames";
import { useState } from "react";
import Avatar from "../Avatar";

export default function UserAvatar({
  name,
  className,
  hoverElement,
}: {
  name?: string;
  className?: string;
  hoverElement?: JSX.Element;
}) {
  const [shouldShowHoverElement, setShouldShowHoverElement] = useState(false);

  return (
    <Avatar
      name={name || ""}
      className={cx(
        "text-xl",
        "bg-gray-200",
        "text-gray-500",
        "border",
        "border-gray-300",
        className
      )}
    >
      {hoverElement && shouldShowHoverElement ? hoverElement : null}
      <Icon
        data-testid={"user-avatar-icon"}
        onMouseEnter={() => setShouldShowHoverElement(true)}
        onMouseLeave={() => setShouldShowHoverElement(false)}
        name="user"
      />
    </Avatar>
  );
}
