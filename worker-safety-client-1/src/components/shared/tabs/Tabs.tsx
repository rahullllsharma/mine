import type { IconName } from "@urbint/silica";
import cx from "classnames";
import { Tab } from "@headlessui/react";
import TabItem from "./tabItem/TabItem";
import { parseOptions } from "./utils";

export type ItemClasses = {
  default: string;
  selected: string;
  unselected: string;
};

export type TabsOption = {
  id?: string | number;
  name: string;
  icon?: IconName;
  hidden?: boolean;
};

export type TabsProps = {
  options: TabsOption[] | string[];
  itemClasses?: ItemClasses;
  direction?: "row" | "col";
  defaultIndex?: number;
  selectedIndex?: number;
  onSelect: (index: number, option: string) => void;
  type?: "regular" | "menu";
};

export default function Tabs({
  itemClasses = {
    default: "",
    selected: "",
    unselected: "",
  },
  direction = "row",
  options,
  defaultIndex = 0,
  selectedIndex,
  type = "regular",
  onSelect,
}: TabsProps): JSX.Element {
  const getItemStyles = (selected?: boolean, isHidden?: boolean) =>
    cx(itemClasses.default, {
      [itemClasses.selected]: selected,
      [itemClasses.unselected]: !selected,
      hidden: !!isHidden,
    });

  const directionStyles = cx("flex", {
    ["flex-col"]: direction === "col",
    ["h-full w-full"]: type === "menu",
  });
  const tabOptions: TabsOption[] = parseOptions(options);

  const itemChangedHandler = (index: number) =>
    onSelect(index, tabOptions[index].name);

  return (
    <Tab.Group
      manual
      {...(selectedIndex === undefined ? { defaultIndex } : { selectedIndex })}
      onChange={itemChangedHandler}
    >
      <Tab.List className={directionStyles}>
        {tabOptions.map(option => (
          <Tab
            className={cx("min-w-0 z-10 outline-none", {
              ["w-1/3"]: type === "menu",
              ["w-0"]: type === "menu" && option.name === "placeholder tab",
            })}
            key={option.name}
          >
            {({ selected }) => (
              <TabItem
                icon={option?.icon}
                value={option.name}
                type={type}
                className={getItemStyles(selected, option.hidden)}
              />
            )}
          </Tab>
        ))}
      </Tab.List>
    </Tab.Group>
  );
}
