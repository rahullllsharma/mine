import type { RiskLevel } from "@/api/generated/types";
import type { Hazard } from "@/api/codecs";
import { useState } from "react";
import TaskCard from "@/components/layout/taskCard/TaskCard";
import TaskHeader from "@/components/layout/taskCard/header/TaskHeader";
import TaskContent from "@/components/layout/taskCard/content/TaskContent";
import {
  convertRiskLevelToRiskBadgeRiskLevel,
  getBorderColorByRiskLevel,
} from "../TaskCard/utils";

export type CardProps = {
  name: string;
  riskLevel?: RiskLevel;
  hazards: Hazard[];
};

const Card = ({ name, riskLevel, hazards }: CardProps) => {
  const [isOpen, setIsOpen] = useState(false);
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

export { Card };
