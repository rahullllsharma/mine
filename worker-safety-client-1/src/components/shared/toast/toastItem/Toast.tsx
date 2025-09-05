import type { IconName } from "@urbint/silica";
import cx from "classnames";
import { Icon } from "@urbint/silica";

export type ToastProps = {
  type?: ToastType;
  message: string;
  onDismiss: () => void;
};

export type ToastType = "success" | "warning" | "info" | "error";

const TOAST_ICONS: Record<ToastType, IconName> = {
  success: "circle_check",
  error: "error",
  warning: "warning",
  info: "info_circle",
} as const;

export default function Toast({
  type,
  message,
  onDismiss,
}: ToastProps): JSX.Element {
  const backgroundStyles = cx({
    ["bg-system-error-40"]: type === "error",
    ["bg-system-warning-40"]: type === "warning",
    ["bg-system-info-40"]: type === "info",
    ["bg-system-success-40"]: type === "success",
  });

  const icon = !!type && TOAST_ICONS[type];

  return (
    <button
      className="px-3 py-2 bg-brand-urbint-60 inline-flex items-center rounded shadow-30"
      onClick={onDismiss}
    >
      {icon && (
        <div
          className={cx(
            "mr-2 w-6 h-6 rounded flex items-center justify-center flex-shrink-0",
            backgroundStyles
          )}
        >
          <Icon name={icon} className="text-lg text-white" />
        </div>
      )}
      <p className="text-neutral-light-100 text-base text-left">{message}</p>
    </button>
  );
}
