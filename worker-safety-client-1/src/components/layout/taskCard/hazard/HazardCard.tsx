import type { PropsWithChildren, ReactNode } from "react";

type HazardCardContentProp = PropsWithChildren<{
  header?: ReactNode;
}>;

export default function HazardCard({
  header,
  children,
}: HazardCardContentProp): JSX.Element {
  return (
    <div
      className="text-base text-neutral-shade-100 mb-2"
      data-testid="hazardCard"
    >
      <header className="flex flex-1 text-brand-gray-80  py-2 pr-2 mr-1 font-semibold">
        {header}
      </header>
      {children}
    </div>
  );
}
