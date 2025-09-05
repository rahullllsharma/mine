import type { IconName } from "@urbint/silica";
import type { NavigationStatus } from "../Navigation";
import cx from "classnames";
import { Icon } from "@urbint/silica";
import { getNavigationItemStyles, getNavigationStyles } from "../utils";

export type NavigationSelectMarker = "full" | "left";
export type NavigationIconSize = "lg" | "xl";

export type NavItemProps = {
  name: string;
  status?: NavigationStatus;
  isSelected?: boolean;
  markerType?: NavigationSelectMarker;
  as?: "div" | "li";
  icon?: IconName;
  iconSize?: NavigationIconSize;
  isSubStep?: boolean;
};

export default function NavItem({
  name,
  status = "default",
  isSelected = false,
  markerType = "full",
  as: As = "div",
  icon,
  iconSize = "xl",
  isSubStep = false,
  ...props
}: NavItemProps): JSX.Element {
  const { iconColor, background, border, marker } = getNavigationStyles(status);
  const showLateralMarker = markerType === "left" && isSelected;

  return (
    <As
      {...props}
      className={getNavigationItemStyles(
        background,
        border,
        markerType,
        isSelected,
        isSubStep
      )}
    >
      {showLateralMarker && (
        <div
          className={cx(
            "absolute top-0 -left-px bottom-0 w-1 h-full rounded-l-none rounded-r-xl",
            marker
          )}
        />
      )}
      {icon && (
        <Icon name={icon} className={cx(`text-${iconSize} mr-1`, iconColor)} />
      )}
      <span className="text-base mx-1 truncate">{name}</span>
    </As>
  );
}
