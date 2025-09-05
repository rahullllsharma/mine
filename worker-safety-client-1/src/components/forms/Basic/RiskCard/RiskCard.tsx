/* eslint-disable @next/next/no-img-element */
import type { CriticalRisk } from "@/api/codecs";
import classnames from "classnames";

export type RiskCardProps = {
  headerClassName?: string;
  className?: string;
  risk: CriticalRisk;
  onClick?: () => void;
};

const riskLabel = (risk: CriticalRisk): string => {
  switch (risk) {
    case "ArcFlash":
      return "Arc Flash";
    case "CollisionLossOfControl":
      return "Collision Loss of Control";
    case "ConfinedSpace":
      return "Enclosed or Confined Space";
    case "ExposureToEnergy":
      return "Exposure to Energy";
    case "FallOrFallArrest":
      return "Fall or Fall Arrest";
    case "FireOrExplosion":
      return "Fire or Explosion";
    case "HoistedLoads":
      return "Hoisted Loads";
    case "LineOfFire":
      return "Line of Fire";
    case "MobileEquipment":
      return "Mobile Equipment";
    case "TrenchingOrExcavation":
      return "Trenching or Excavation";
  }
};

const riskImageSrc = (risk: CriticalRisk): string => `/assets/JSB/${risk}.svg`;

const RiskCard: React.FC<RiskCardProps> = ({
  className,
  headerClassName,
  children,
  risk,
  onClick, // Added onClick prop to check the entire card
}) => {
  const handleClick = () => {
    if (onClick) {
      onClick(); // Call the onClick function passed from RiskToggleCard
    }
  };
  return (
    <div
      className={classnames(
        "max-w-[231px] shadow-10 rounded-lg cursor-pointer",
        className
      )}
      onClick={handleClick} // Attached onClick handler to the check or uncheck the card
    >
      <div className={classnames("bg-white px-4 py-2", headerClassName)}>
        <span className="text-base font-semibold">{riskLabel(risk)}</span>
      </div>

      <div className="flex flex-col items-center p-4 bg-white">
        <img className="pb-2" src={riskImageSrc(risk)} alt="Risk image" />
        <span className="pb-2 text-sm font-semibold">
          Critical risk observed
        </span>
        {children}
      </div>
    </div>
  );
};

export { RiskCard };
