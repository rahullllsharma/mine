import type { PropsWithChildren } from "react";

type FilterWrapperProps = PropsWithChildren<{
  title: string;
}>;

export default function FilterWrapper({
  title,
  children,
}: FilterWrapperProps): JSX.Element {
  return (
    <div>
      <span className="text-sm text-neutral-shade-100">{title}</span>
      {children}
    </div>
  );
}
