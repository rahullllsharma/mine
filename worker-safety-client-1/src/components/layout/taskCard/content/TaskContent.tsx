import type { Hazard } from "@/types/project/Hazard";
import type { Control } from "@/types/project/Control";
import HazardCard from "../hazard/HazardCard";
import ControlCard from "../control/ControlCard";

function ControlCards({ controls }: { controls: Control[] }) {
  return (
    <>
      {controls.map(({ id, name }) => (
        <ControlCard className="mt-2 first:mt-0" key={id} label={name} />
      ))}
    </>
  );
}

type HazardCardProps = {
  hazards: Hazard[];
};

export default function TaskContent({
  hazards = [],
}: HazardCardProps): JSX.Element {
  return (
    <div className="bg-brand-gray-10 px-4 py-2">
      {hazards.map(({ id, name, controls }) => (
        <HazardCard key={id} header={name}>
          <ControlCards controls={controls} />
        </HazardCard>
      ))}
    </div>
  );
}
