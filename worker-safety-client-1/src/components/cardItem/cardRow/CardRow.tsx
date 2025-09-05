import type { PropsWithChildren } from "react";

type CardRowProps = PropsWithChildren<{ label: string }>;

export default function CardRow({
  label,
  children,
}: CardRowProps): JSX.Element {
  return (
    <div className="flex items-center border-solid border-t py-1.5 text-sm text-neutral-shade-75">
      <span className="flex-1 font-semibold">{label}</span>
      {children}
    </div>
  );
}
