import type { TaskCardProps } from "../../templatesComponents/customisedForm.types";
import classnames from "classnames";
import { ActionLabel } from "@urbint/silica";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import Button from "@/components/shared/button/Button";
import RiskBadge from "../../riskBadge/RiskBadge";
import { TagCard } from "../../forms/Basic/TagCard";
import { getBorderColorByRiskLevel } from "../../../utils/risk";

const CWFTaskCard = ({
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
}: TaskCardProps) => {
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
          <ActionLabel className={"text-base"}>{title}</ActionLabel>
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
};

export { CWFTaskCard };
