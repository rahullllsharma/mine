import type { RiskLevel } from "@/api/generated/types";
import type { ReactNode } from "react";
import classnames from "classnames";

import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import Button from "@/components/shared/button/Button";
import { TagCard } from "../TagCard";
import { RiskBadge } from "./RiskBadge";
import { getBorderColorByRiskLevel } from "./utils";

export type TaskCardProps = {
  className?: string;
  title: string;
  risk: RiskLevel;
  expandable?: boolean;
  isExpanded?: boolean;
  toggleElementExpand?: () => void;
  showRiskInformation?: boolean;
  showRiskText?: boolean;
  withLeftBorder?: boolean;
  onClickEdit?: () => void;
  children?: ReactNode;
  isReadOnly?: boolean;
};

function TaskCard({
  className,
  title,
  risk,
  expandable = false,
  isExpanded = false,
  toggleElementExpand,
  showRiskInformation = true,
  showRiskText = true,
  withLeftBorder = true,
  onClickEdit,
  children,
  isReadOnly = false,
}: TaskCardProps) {
  return (
    <TagCard
      withLeftBorder={withLeftBorder}
      className={classnames(
        "justify-between items-center gap-2",
        showRiskInformation && getBorderColorByRiskLevel(risk),
        className
      )}
    >
      <div className="flex flex-col w-full gap-2">
        <div className="flex flex-row justify-start items-center w-full gap-2">
          {expandable && (
            <ButtonIcon
              onClick={toggleElementExpand}
              iconName={isExpanded ? "chevron_down" : "chevron_right"}
            />
          )}
          <span className="text-base text-neutral-shade-100 font-semibold">
            {title}
          </span>
          <div className="flex ml-auto justify-between gap-4">
            {showRiskInformation && (
              <RiskBadge
                risk={risk}
                label={`${risk}${showRiskText ? " risk" : ""}`}
              />
            )}
            {onClickEdit && !isReadOnly && (
              <Button
                onClick={onClickEdit}
                className="text-brand-urbint-50 flex items-center gap-1"
                label="edit"
                iconStart="edit"
              />
            )}
          </div>
        </div>
        {isExpanded && children}
      </div>
    </TagCard>
  );
}

export { TaskCard };
