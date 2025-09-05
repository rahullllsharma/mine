import type {
  NavigationOption,
  NavigationStatus,
} from "../navigation/Navigation";
import { Tab } from "@headlessui/react";
import NavItem from "../navigation/navItem/NavItem";

type SidebarProps = {
  options: NavigationOption[];
  selectedIndex: number;
  onChange: (index: number) => void;
};

const getBackgroundColor = (status: NavigationStatus = "default") =>
  status === "default" ? "bg-neutral-shade-3" : undefined;

//The Sidebar is updated via prop (instead of internal state) to allow the parent to control the state (which will be needed for the DIR)
export default function Sidebar({
  options,
  selectedIndex,
  onChange,
}: SidebarProps): JSX.Element {
  const index = selectedIndex < options.length ? selectedIndex : 0;
  return (
    <Tab.Group manual vertical selectedIndex={index} onChange={onChange}>
      <Tab.List className="flex flex-col gap-2">
        {options.map(({ id, icon, name, status, iconSize }) => {
          return (
            <Tab className={getBackgroundColor(status)} key={id}>
              {({ selected }) => (
                <NavItem
                  icon={icon}
                  iconSize={iconSize}
                  name={name}
                  status={status}
                  isSelected={selected}
                />
              )}
            </Tab>
          );
        })}
      </Tab.List>
    </Tab.Group>
  );
}
