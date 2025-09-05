import type { TaskFormControl } from "@/types/task/TaskFormControl";
import Switch from "@/components/switch/Switch";
import ControlCard from "../../control/ControlCard";

type ControlCardContentProps = {
  control: TaskFormControl;
  isActive: boolean;
  isDisabled?: boolean;
  onToggle: (state: boolean) => void;
};

export default function ControlCardContent({
  control,
  isActive,
  onToggle,
  isDisabled = false,
}: ControlCardContentProps): JSX.Element {
  return (
    <ControlCard label={control.name}>
      <Switch
        title={`${control.name}-switch`}
        stateOverride={isActive}
        onToggle={onToggle}
        isDisabled={isDisabled}
      />
    </ControlCard>
  );
}
