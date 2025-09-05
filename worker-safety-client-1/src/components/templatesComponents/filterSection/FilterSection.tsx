import type { PropsWithChildren } from "react";
import Accordion from "@/components/shared/accordion/Accordion";

type FilterSectionProps = PropsWithChildren<{
  title: string;
  count?: number;
}>;

export default function FilterSection({
  title,
  count,
  children,
}: FilterSectionProps): JSX.Element {
  const countMessage = count ? `(${count})` : "";

  return (
    <Accordion
      unmount={false}
      headerClassName="p-3 border-b border-solid border-brand-gray-20"
      header={
        <span
          role="heading"
          aria-level={6}
          className="text-base font-semibold text-neutral-shade-75"
        >
          {`${title} ${countMessage}`}
        </span>
      }
    >
      <div className="p-3">{children}</div>
    </Accordion>
  );
}
