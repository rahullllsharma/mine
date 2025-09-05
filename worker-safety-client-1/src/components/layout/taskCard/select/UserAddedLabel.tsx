import cx from "classnames";

export default function UserAddedLabel({
  label,
  className,
}: {
  label: string;
  className?: string;
}) {
  return (
    <p
      className={cx(
        "text-sm",
        "font-light",
        "border",
        "rounded-md",
        "bg-black",
        "text-white",
        "w-max",
        "px-2",
        "py-1",
        className
      )}
    >
      {label}
    </p>
  );
}
