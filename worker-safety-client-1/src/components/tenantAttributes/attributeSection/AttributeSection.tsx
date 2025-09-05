import type { PropsWithChildren } from "react";
import cx from "classnames";
import { Icon } from "@urbint/silica";
import Tooltip from "@/components/shared/tooltip/Tooltip";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";

type AttributeSectionProps = PropsWithChildren<{
  label: string;
  defaultLabel: string;
  onEditClick: () => void;
}>;

function AttributeSection({
  label,
  defaultLabel,
  children,
  onEditClick,
}: AttributeSectionProps): JSX.Element {
  const isTooltipVisible = defaultLabel !== label;

  return (
    <div className="p-3 bg-brand-gray-10">
      <div className={cx("flex items-center", { "mb-6": children })}>
        <h3 className="text-lg font-semibold flex gap-2">
          {label}
          {isTooltipVisible && (
            <Tooltip title={`Original value: "${defaultLabel}"`} position="top">
              <Icon
                aria-label="attribute-tooltip"
                name="info_circle"
                className="text-xl leading-5"
              />
            </Tooltip>
          )}
        </h3>
        <ButtonIcon
          iconName="edit"
          className="p-1 ml-3"
          onClick={onEditClick}
        />
      </div>
      {children}
    </div>
  );
}

export { AttributeSection };
