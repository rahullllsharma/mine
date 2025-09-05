import type { PopupProps } from "react-map-gl";
import type { PropsWithClassName } from "@/types/Generic";

import { Popup } from "react-map-gl";
import cx from "classnames";

type MapPopupProps = PropsWithClassName<
  Pick<PopupProps, "longitude" | "latitude" | "onClose" | "children">
>;

export default function MapPopup({
  longitude,
  latitude,
  onClose,
  children,
  className,
}: MapPopupProps): JSX.Element {
  return (
    <Popup
      offset={12}
      className={cx("max-w-7xl", className)}
      longitude={longitude}
      latitude={latitude}
      closeButton={false}
      onClose={onClose}
      maxWidth={undefined}
    >
      {children}
    </Popup>
  );
}
