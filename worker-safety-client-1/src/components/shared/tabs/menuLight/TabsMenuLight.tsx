import type { ItemClasses, TabsOption, TabsProps } from "../Tabs";
import Tabs from "../Tabs";

export default function TabsMenuLight({
  options,
  defaultIndex,
  selectedIndex,
  onSelect,
}: Omit<TabsProps, "itemClasses" | "options"> & {
  options: Pick<TabsOption, "id" | "name">[] | string[];
  selectedIndex?: number;
}): JSX.Element {
  const itemClasses: ItemClasses = {
    default: "text-sm text-neutral-shade-100 box-border",
    selected:
      "border-t-2 border-solid border-brand-urbint-40 text-neutral-shade-100",
    unselected: "text-neutral-shade-58",
  };

  return (
    <>
      <Tabs
        itemClasses={itemClasses}
        options={options}
        defaultIndex={defaultIndex}
        selectedIndex={selectedIndex}
        onSelect={onSelect}
        type="menu"
      />
    </>
  );
}
