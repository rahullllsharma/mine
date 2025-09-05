import Switch from "@/components/switch/Switch";

type HazardHeadContentProps = {
  label: string;
  isActive: boolean;
  isDisabled?: boolean;
  onToggle: (state: boolean) => void;
};

export default function HazardHeaderContent({
  label,
  isActive,
  isDisabled = false,
  onToggle,
}: HazardHeadContentProps): JSX.Element {
  return (
    <>
      <p className="flex-1">{label}</p>
      <Switch
        title={`${label}-switch`}
        stateOverride={isActive}
        onToggle={onToggle}
        isDisabled={isDisabled}
      />
    </>
  );
}
