import type { RiskLevel } from "@/components/riskBadge/RiskLevel";
import LocationRiskIcon from "../../locationRiskIcon/LocationRiskIcon";

export type RiskLegendItemProps = {
  riskLevel: RiskLevel;
  legend: string;
};

export default function RiskLegendItem({
  riskLevel,
  legend = "",
}: RiskLegendItemProps): JSX.Element {
  return (
    <li className="flex gap-2 items-center">
      <LocationRiskIcon riskLevel={riskLevel} label={legend} />
      {/* TODO: replace this with the TextCaption component */}
      <p className="text-tiny">{legend}</p>
    </li>
  );
}
