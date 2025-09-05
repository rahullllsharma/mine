import type { ItemClasses, TabsOption, TabsProps } from "../Tabs";
import Tabs from "../Tabs";

export default function TabsDark({
  options,
  defaultIndex,
  selectedIndex,
  onSelect,
}: Omit<TabsProps, "itemClasses" | "options"> & {
  options: Pick<TabsOption, "id" | "name">[] | string[];
  selectedIndex?: number;
}): JSX.Element {
  const itemClasses: ItemClasses = {
    default: "text-white font-semibold border-b-2",
    selected: "border-brand-urbint-40 border-solid z-10",
    unselected: "opacity-75 border-transparent",
  };

  return (
    <Tabs
      itemClasses={itemClasses}
      options={options}
      defaultIndex={defaultIndex}
      selectedIndex={selectedIndex}
      onSelect={onSelect}
    />
  );
}
