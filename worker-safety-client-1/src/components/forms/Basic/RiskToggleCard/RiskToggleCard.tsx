import type { ToggleProps } from "../Toggle/Toggle";
import type { CriticalRisk } from "@/api/codecs";
import { constVoid } from "fp-ts/lib/function";
import { Toggle } from "../Toggle/Toggle";
import { RiskCard } from "../RiskCard";

export type RiskToggleCardProps = ToggleProps & {
  risk: CriticalRisk;
};

const RiskToggleCard = ({
  risk,
  checked,
  disabled,
  onClick,
}: RiskToggleCardProps) => {
  return (
    <RiskCard
      headerClassName="bg-brand-gray-10"
      risk={risk}
      onClick={disabled ? constVoid : onClick}
    >
      <Toggle checked={checked} onClick={constVoid} />{" "}
      {/* onClick handled by the parent component */}
    </RiskCard>
  );
};

export { RiskToggleCard };
