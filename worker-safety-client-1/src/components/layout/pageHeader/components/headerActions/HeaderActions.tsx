import type { BaseSyntheticEvent, ReactNode } from "react";
import type { IconName } from "@urbint/silica";
import type { MenuItemProps } from "@/components/shared/dropdown/Dropdown";

import { Icon } from "@urbint/silica";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import Dropdown from "@/components/shared/dropdown/Dropdown";
import Tooltip from "@/components/shared/tooltip/Tooltip";

type PageHeaderActionTooltip = {
  title: string;
  icon?: IconName;
  type: "tooltip";
};

type PageHeaderAction = {
  type?: "button";
  icon: IconName;
  title: string;
  rightSlot?: ReactNode;
  onClick: (event: BaseSyntheticEvent) => void;
};

const HeaderActions = ({
  actions,
}: {
  actions: PageHeaderAction[] | [PageHeaderActionTooltip];
}): JSX.Element => {
  if (actions.length === 1) {
    const [action] = actions;

    if (action?.type === "tooltip") {
      return (
        <Tooltip
          title={action.title}
          position="left"
          containerClasses={"inline-block ml-auto hover:cursor-pointer"}
        >
          <Icon
            name={action.icon || "info_circle_outline"}
            className="leading-none text-xl"
            role="tooltip"
          />
        </Tooltip>
      );
    }

    return (
      <ButtonIcon
        iconName={action.icon}
        className="ml-auto leading-5"
        title={action.title}
        onClick={action.onClick}
      />
    );
  }

  const menuItems: MenuItemProps[] = (actions as PageHeaderAction[]).map(
    action => ({
      label: action.title,
      icon: action.icon,
      rightSlot: action.rightSlot,
      onClick: action.onClick,
    })
  );

  return (
    <Dropdown className="ml-auto z-30" menuItems={[menuItems]}>
      <ButtonIcon iconName="more_horizontal" />
    </Dropdown>
  );
};

export type { PageHeaderActionTooltip, PageHeaderAction };
export { HeaderActions };
