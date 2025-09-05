import type { ClusterProperties } from "./clustering.types";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import RiskBadge from "@/components/riskBadge/RiskBadge";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";

type ClusterCardProps = {
  properties: ClusterProperties;
  onCloseClusterCard: () => void;
};

function ClusterCard({ properties, onCloseClusterCard }: ClusterCardProps) {
  return (
    <div className="flex flex-col w-52 p-2 bg-white rounded-lg absolute -bottom-20 inset-x-0 cursor-default">
      {/* locations keyword needs to come from the tenant context */}
      <div className="flex justify-between mb-2">
        <div className="font-medium text-base text-center pl-9">
          {properties.length} Locations
        </div>
        <ButtonIcon
          iconName="close_big"
          className="leading-5"
          onClick={onCloseClusterCard}
          title="Close modal"
        />
      </div>
      <ul className="flex justify-around text-sm font-medium">
        <li>
          <RiskBadge risk={RiskLevel.HIGH} label={properties.HIGH.toString()} />
        </li>
        <li>
          <RiskBadge
            risk={RiskLevel.MEDIUM}
            label={properties.MEDIUM.toString()}
          />
        </li>
        <li>
          <RiskBadge risk={RiskLevel.LOW} label={properties.LOW.toString()} />
        </li>
        <li>
          <RiskBadge
            risk={RiskLevel.UNKNOWN}
            label={`? ${(
              properties.UNKNOWN + properties.RECALCULATING
            ).toString()}`}
          />
        </li>
      </ul>
    </div>
  );
}

export { ClusterCard };
