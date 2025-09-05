import { RiskLevel } from "@/components/riskBadge/RiskLevel";

/**
 * @deprecated
 * @todo remove once silica badge is updated
 */
const getLabelWithRiskIcon = ({
  label,
  risk,
}: {
  label?: string;
  risk?: RiskLevel;
}): string => {
  // FIXME: Some icon fonts like the question mark don't behave like the other icons (lack spacing)
  // Once that's fixed on silica for the Badge component, this can be removed.
  return label
    ? `${risk === RiskLevel.UNKNOWN ? "? " : ""}${label.toUpperCase()}`
    : "";
};

export { getLabelWithRiskIcon };
