import { Checkbox } from "@/components/forms/Basic/Checkbox";
import { useWidgetCount } from "@/context/CustomisedDataContext/CustomisedFormStateContext";

interface WidgetCheckboxProps {
  checked: boolean;
  disabled?: boolean;
  onToggle: (value: boolean) => void;
}

export const WidgetCheckbox = ({
  checked,
  disabled = false,
  onToggle,
}: WidgetCheckboxProps) => {
  const {
    widgetCount,
    maxWidgetCount,
    incrementWidgetCount,
    decrementWidgetCount,
  } = useWidgetCount();

  const handleClick = () => {
    const newValue = !checked;

    // Handle widget count tracking
    if (newValue && !checked) {
      incrementWidgetCount();
    } else if (!newValue && checked) {
      decrementWidgetCount();
    }

    onToggle(newValue);
  };

  const isDisabled = disabled || (!checked && widgetCount >= maxWidgetCount);

  return (
    <Checkbox checked={checked} onClick={handleClick} disabled={isDisabled}>
      <span className="text-brand-gray-80 text-sm">
        Add to widget ({widgetCount}/{maxWidgetCount} added)
      </span>
    </Checkbox>
  );
};
