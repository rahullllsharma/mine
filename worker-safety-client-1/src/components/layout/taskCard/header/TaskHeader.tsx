import type { IconName } from "@urbint/silica";
import type { KeyboardEventHandler } from "react";
import type { MenuItemProps } from "@/components/shared/dropdown/Dropdown";
import type { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { ActionLabel, Badge, Icon } from "@urbint/silica";
import cx from "classnames";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import RiskBadge from "@/components/riskBadge/RiskBadge";
import Tooltip from "@/components/shared/tooltip/Tooltip";
import Dropdown from "@/components/shared/dropdown/Dropdown";

export type TaskHeaderProps = {
  icon?: IconName;
  iconClassName?: string;
  menuIcon?: IconName;
  headerText: string;
  onClick?: () => void;
  onMenuClicked?: () => void;
  showSummaryCount?: boolean;
  totalHazards?: number;
  totalControls?: number;
  subHeaderText?: string;
  riskLevel?: RiskLevel;
  hasInfoIcon?: boolean;
  infoIconTooltipText?: string;
  hasDropdown?: boolean;
  dropdownOptions?: MenuItemProps[][];
};

export default function TaskHeader({
  icon,
  iconClassName,
  menuIcon,
  headerText,
  onClick,
  onMenuClicked,
  showSummaryCount = false,
  totalHazards = 0,
  totalControls = 0,
  subHeaderText,
  riskLevel,
  hasInfoIcon,
  infoIconTooltipText,
  hasDropdown,
  dropdownOptions = [],
}: TaskHeaderProps): JSX.Element {
  const keyPressHandler: KeyboardEventHandler<HTMLDivElement> = e => {
    // https://www.w3.org/TR/uievents-key/#keys-whitespace
    if (e.key === "Enter" || e.key === " ") {
      onClick && onClick();
    }
  };

  return (
    <div className="flex flex-1 items-stretch h-auto p-3">
      <div
        role="button"
        tabIndex={0}
        className={cx(
          "flex flex-1 flex-wrap items-stretch gap-y-3 gap-x-6 md:gap-0 md:flex-row md:flex-nowrap md:items-center mr-6 outline-none",
          { "cursor-default": !onClick }
        )}
        onClick={onClick}
        onKeyPress={keyPressHandler}
      >
        <div className="text-left text-base text-neutral-shade-100 font-bold flex flex-auto m-0 items-center gap-3 w-full md:flex-initial md:gap-4 md:w-auto md:ml-3 md:mr-4">
          {icon && (
            <Icon name={icon} className={cx("text-xl", iconClassName)} />
          )}
          <div>
            <ActionLabel className="font-semibold">{headerText}</ActionLabel>
            {subHeaderText && (
              <span className=" pl-1 text-tiny font-medium text-neutral-shade-58">
                {subHeaderText}
              </span>
            )}
          </div>
          {hasInfoIcon && (
            <Tooltip title={infoIconTooltipText ?? ""} position="right">
              <Icon name="info_circle_outline" />
            </Tooltip>
          )}
        </div>
        {riskLevel && (
          <Tooltip
            title={
              "The High / Medium / Low classification represents the relative likelihood of presence of high energy hazards while the task is being performed"
            }
            position="bottom"
            className="max-w-xl"
          >
            <RiskBadge risk={riskLevel} label={`${riskLevel}`} />
          </Tooltip>
        )}
        {showSummaryCount && (
          <div className="flex flex-1 justify-start md:justify-center ml-2">
            <Badge label={`${totalHazards}H`} className="mr-2" />
            <Badge label={`${totalControls}C`} />
          </div>
        )}
      </div>
      {/*Menu button*/}
      {!hasDropdown && onMenuClicked && menuIcon && (
        <ButtonIcon
          iconName={menuIcon}
          onClick={onMenuClicked}
          title="Menu button"
          className="flex items-center self-center px-2.5 py-2"
        />
      )}
      {hasDropdown && dropdownOptions.length > 0 && (
        <Dropdown menuItems={dropdownOptions}>
          <ButtonIcon iconName="more_horizontal" className="h-full" />
        </Dropdown>
      )}
    </div>
  );
}
