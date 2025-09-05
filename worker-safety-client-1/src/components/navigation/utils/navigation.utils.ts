import type { NavigationStatus } from "../../navigation/Navigation";
import type { NavigationSelectMarker } from "../navItem/NavItem";
import cx from "classnames";

export type NavigationStyles = {
  iconColor: string;
  background: string;
  border: string;
  marker: string;
};

export const defaultNavigationStyles: Readonly<NavigationStyles> = {
  iconColor: "text-neutral-shade-75",
  background: "",
  border: "border-neutral-shade-100",
  marker: "bg-neutral-shade-75",
};

export const completedNavigationStyles: Readonly<NavigationStyles> = {
  iconColor: "text-brand-urbint-40",
  background: "bg-brand-urbint-10",
  border: "border-brand-urbint-30",
  marker: "bg-brand-urbint-40",
};

export const errorNavigationStyles: Readonly<NavigationStyles> = {
  iconColor: "text-system-error-40",
  background: "bg-system-error-10",
  border: "border-system-error-30",
  marker: "bg-system-error-40",
};

export const getNavigationStyles = (
  status?: NavigationStatus
): NavigationStyles => {
  switch (status) {
    case "completed":
    case "saved":
    case "saved_current":
      return completedNavigationStyles;
    case "error":
      return errorNavigationStyles;
    default:
      return defaultNavigationStyles;
  }
};

export const getNavigationItemStyles = (
  backgroundColor: string,
  borderColor: string,
  markerType: NavigationSelectMarker,
  selected = false,
  isSubStep = false
): string =>
  cx(
    "relative flex items-center px-2.5 py-3 rounded h-12 w-full hover:shadow-10 border-2 text-neutral-shade-100 cursor-pointer",
    backgroundColor,
    {
      [borderColor]: selected && markerType === "full",
      ["border-transparent"]: !selected || markerType === "left",
      ["pl-8"]: isSubStep,
    }
  );
