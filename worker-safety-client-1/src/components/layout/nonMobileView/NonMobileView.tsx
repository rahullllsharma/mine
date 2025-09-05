import type { CustomViewProps } from "react-device-detect";
import { isMobile, CustomView } from "react-device-detect";

export function NonMobileView({
  condition,
  children,
}: CustomViewProps): JSX.Element {
  return <CustomView condition={!isMobile && condition}>{children}</CustomView>;
}
