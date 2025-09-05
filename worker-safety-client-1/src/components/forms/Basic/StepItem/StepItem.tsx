import type { IconName } from "@urbint/silica";
import { Icon } from "@urbint/silica";
import classnames from "classnames";

export type Status =
  | "default"
  | "current"
  | "saved"
  | "saved_current"
  | "error";

type StepItemProps = {
  status?: Status;
  truncate?: boolean;
  label: string;
  onClick: () => void;
};

type StatusIconClassName = {
  [key in Status]: {
    icon: IconName;
    iconClassName?: string;
    buttonClassName?: string;
  };
};

const statusIconClassNames: StatusIconClassName = {
  default: {
    icon: "circle",
    iconClassName: "text-neutral-shade-58",
    buttonClassName: "border-2 border-transparent box-border",
  },
  current: {
    icon: "circle",
    iconClassName: "text-neutral-shade-58",
    buttonClassName: "border-2 border-neutral-shade-100 box-border",
  },
  saved: {
    icon: "circle_check",
    iconClassName: "text-brand-urbint-40",
    buttonClassName: "border-2 border-transparent bg-brand-urbint-10",
  },
  saved_current: {
    icon: "circle_check",
    iconClassName: "text-brand-urbint-40",
    buttonClassName:
      "border-2 bg-brand-urbint-10 border-brand-urbint-30 box-border",
  },
  error: {
    icon: "error",
    iconClassName: "text-system-error-40",
    buttonClassName:
      "border-2 border-system-error-40 bg-system-error-10 box-border",
  },
};

const StepItem = ({
  label,
  status = "default",
  truncate = false,
  onClick,
}: StepItemProps) => {
  const { icon, iconClassName, buttonClassName } = statusIconClassNames[status];

  return (
    <button
      className={classnames(
        "p-3 bg-neutral-shade-3 rounded flex w-full items-center text-left",
        buttonClassName
      )}
      onClick={onClick}
    >
      <Icon name={icon} className={iconClassName} />
      <span
        className={classnames(
          "ml-2 text-base font-normal text-neutral-shade-100",
          { ["truncate"]: truncate }
        )}
      >
        {label}
      </span>
    </button>
  );
};

export { StepItem };
