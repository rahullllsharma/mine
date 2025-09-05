import type { ItemClasses, TabsOption, TabsProps } from "../Tabs";
import Tabs from "../Tabs";

export default function TabsLight({
  options,
  defaultIndex,
  onSelect,
}: Omit<TabsProps, "itemClasses" | "options"> & {
  options: Pick<TabsOption, "id" | "name">[] | string[];
}): JSX.Element {
  const itemClasses: ItemClasses = {
    default:
      "text-neutral-shade-75 font-semibold active:bg-neutral-shade-3 border-b-4",
    selected: "border-brand-urbint-40 border-solid z-10",
    unselected: "opacity-75 border-transparent",
  };

  return (
    <>
      <Tabs
        itemClasses={itemClasses}
        options={options}
        defaultIndex={defaultIndex}
        onSelect={onSelect}
      />
      <hr
        className="relative bg-neutral-shade-18 z-1 border"
        style={{
          bottom: "3px",
        }}
      />
    </>
  );
}
