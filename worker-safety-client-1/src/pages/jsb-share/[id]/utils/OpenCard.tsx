import type { RiskLevel } from "@/api/generated/types";
import type { Hazard } from "@/api/codecs";
import { useState } from "react";
import TaskCard from "@/components/layout/taskCard/TaskCard";
import TaskHeader from "@/components/layout/taskCard/header/TaskHeader";
import TaskContent from "@/components/layout/taskCard/content/TaskContent";
import {
  convertRiskLevelToRiskBadgeRiskLevel,
  getBorderColorByRiskLevel,
} from "@/components/forms/Basic/TaskCard/utils";

export type OpenCardProps = {
  name: string;
  riskLevel?: RiskLevel;
  hazards: Hazard[];
};

const OpenCard = ({ name, riskLevel, hazards }: OpenCardProps) => {
  const [isOpen, setIsOpen] = useState(true);
  const handleClick = () => setIsOpen(!isOpen);

  return (
    <TaskCard
      isOpen={isOpen}
      className={
        riskLevel ? getBorderColorByRiskLevel(riskLevel) : "border-data-blue-30"
      }
      taskHeader={
        <TaskHeader
          icon={isOpen ? "chevron_big_up" : "chevron_big_down"}
          headerText={name}
          riskLevel={
            riskLevel
              ? convertRiskLevelToRiskBadgeRiskLevel(riskLevel)
              : undefined
          }
          onClick={handleClick}
        />
      }
    >
      <TaskContent hazards={hazards} />
    </TaskCard>
  );
};

export default OpenCard;
