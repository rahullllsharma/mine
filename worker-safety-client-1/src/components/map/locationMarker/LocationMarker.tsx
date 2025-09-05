import type { PropsWithClassName } from "@/types/Generic";
import type { RiskLevel } from "@/components/riskBadge/RiskLevel";
import type { MouseEventHandler } from "react";
import type { MapboxEvent, MarkerProps } from "react-map-gl";
import { Marker } from "react-map-gl";
import LocationRiskIcon from "../locationRiskIcon/LocationRiskIcon";

export type LocationMarkerEvent = MapboxEvent<MouseEvent>;

export type LocationMarkerProps = PropsWithClassName<
  Pick<MarkerProps, "latitude" | "longitude" | "onClick">
> & {
  riskLevel: RiskLevel;
  isActive?: boolean;
  onMouseEnter?: MouseEventHandler<HTMLDivElement>;
  onMouseLeave?: () => void;
  isCritical?: boolean;
};

export default function LocationMarker({
  riskLevel,
  latitude,
  longitude,
  isActive = false,
  onClick,
  onMouseEnter,
  onMouseLeave,
  isCritical = false,
}: LocationMarkerProps): JSX.Element {
  return (
    <div
      data-testid="map-marker"
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      <Marker longitude={longitude} latitude={latitude} onClick={onClick}>
        <LocationRiskIcon
          riskLevel={riskLevel}
          label="badge"
          isActive={isActive}
          isCritical={isCritical}
        />
      </Marker>
    </div>
  );
}
