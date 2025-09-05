import type { ReactNode } from "react";

export default function Labeled({
  label,
  children,
  className,
}: {
  label: string;
  children: ReactNode;
  className?: string;
}): JSX.Element {
  return (
    <div className="flex flex-col gap-2">
      <label className="block text-tiny md:text-sm font-semibold leading-normal">
        {label}
      </label>
      {className ? (
        <div className={className}>{children}</div>
      ) : (
        <div>{children}</div>
      )}
    </div>
  );
}
