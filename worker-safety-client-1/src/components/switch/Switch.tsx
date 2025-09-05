import { useEffect, useState } from "react";
import { Switch as HeadlessUiSwitch } from "@headlessui/react";

export type SwitchProps = {
  stateOverride?: boolean;
  isDisabled?: boolean;
  title?: string;
  onToggle: (state: boolean) => void;
};

export default function Switch({
  onToggle,
  title = "Toggle",
  isDisabled,
  stateOverride = false,
}: SwitchProps): JSX.Element {
  const [isEnabled, setIsEnabled] = useState(stateOverride ?? false);

  const toggleHandler = (value: boolean) => {
    setIsEnabled(value);
    onToggle(value);
  };

  useEffect(() => {
    setIsEnabled(stateOverride);
  }, [stateOverride]);

  return (
    <HeadlessUiSwitch
      checked={isEnabled}
      onChange={toggleHandler}
      disabled={isDisabled}
      className="relative inline-flex items-center h-6 rounded-full w-11 bg-white outline-none border border-brand-gray-40 disabled:opacity-38 disabled:cursor-not-allowed focus:border-brand-gray-50"
    >
      <span className="sr-only">{title}</span>
      <span
        className={`${
          isEnabled
            ? "translate-x-6 print-translate-x-6 bg-system-success-40"
            : "translate-x-0.5 print-translate-x-0.5 bg-brand-gray-40"
        } inline-block w-4 h-4 rounded-full`}
      />
    </HeadlessUiSwitch>
  );
}
