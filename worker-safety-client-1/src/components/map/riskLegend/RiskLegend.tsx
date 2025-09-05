import type { PropsWithClassName } from "@/types/Generic";
import type { MapLegendProps } from "../mapLegend/MapLegend";
import React from "react";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import MapLegend from "../mapLegend/MapLegend";
import Tooltip from "../../shared/tooltip/Tooltip";
import RiskLegendItem from "./riskLegendItem/RiskLegendItem";

export type RiskLegendProps = Pick<PropsWithClassName, "className"> & {
  label: MapLegendProps["header"];
  position?: MapLegendProps["position"];
};

export default function RiskLegend({
  label,
  className,
  position = "bottom-right",
}: RiskLegendProps): JSX.Element {
  return (
    <MapLegend
      position={position}
      header={label}
      className={className}
      isDefaultOpen
    >
      <div>
        <ul className="flex flex-col gap-2">
          <Tooltip
            title={`The High / Medium / Low classification represents the relative likelihood of presence of high energy hazards while the task is being performed`}
            position="right"
            className={"w-6/12 right-48 !left-auto !top-auto bottom-0"}
          >
            <RiskLegendItem riskLevel={RiskLevel.HIGH} legend="High" />
          </Tooltip>

          <Tooltip
            title={`The High / Medium / Low classification represents the relative likelihood of presence of high energy hazards while the task is being performed`}
            position="right"
            className={"w-6/12 right-48 !left-auto !top-auto bottom-0"}
          >
            <RiskLegendItem riskLevel={RiskLevel.MEDIUM} legend="Medium" />
          </Tooltip>
          <Tooltip
            title={`The High / Medium / Low classification represents the relative likelihood of presence of high energy hazards while the task is being performed`}
            position="right"
            className={"w-6/12 right-48 !left-auto !top-auto bottom-0"}
          >
            <RiskLegendItem riskLevel={RiskLevel.LOW} legend="Low" />
          </Tooltip>
          <Tooltip
            title={`The High / Medium / Low classification represents the relative likelihood of presence of high energy hazards while the task is being performed`}
            position="right"
            className={"w-6/12 right-48 !left-auto !top-auto bottom-0"}
          >
            <RiskLegendItem riskLevel={RiskLevel.UNKNOWN} legend="Unknown" />
          </Tooltip>
        </ul>
      </div>
    </MapLegend>
  );
}
