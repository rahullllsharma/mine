import Switch from "@/components/switch/Switch";
import { useMapContext } from "../context/MapProvider";

type MapLayerItemProps = {
  title: string;
  onToggle: (state: boolean) => void;
  isChecked: boolean;
};

export function MapLayerItem({
  title,
  onToggle,
  isChecked,
}: MapLayerItemProps): JSX.Element {
  return (
    <div className="flex items-center justify-between">
      <p className="text-tiny text-neutral-shade-100">{title}</p>
      <Switch onToggle={onToggle} stateOverride={isChecked} />
    </div>
  );
}

export default function MapLayersMenu(): JSX.Element {
  const { riskLegend, satelliteView } = useMapContext();

  return (
    <div className="p-3 rounded bg-white">
      <p className="mb-4 text-sm font-semibold text-neutral-shade-75">
        Manage map layers
      </p>
      <div className="grid gap-y-2">
        <MapLayerItem
          title="Show legend"
          onToggle={riskLegend.toggle}
          isChecked={riskLegend.isActive}
        />
        <MapLayerItem
          title="Show satellite"
          onToggle={satelliteView.toggle}
          isChecked={satelliteView.isActive}
        />
      </div>
    </div>
  );
}
