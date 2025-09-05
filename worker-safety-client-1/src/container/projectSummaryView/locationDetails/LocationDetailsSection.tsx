import type { PropsWithChildren } from "react";
import Accordion from "@/components/shared/accordion/Accordion";

type LocationDetailsSectionProps = PropsWithChildren<{
  title: string;
  isAccordionOpen?: boolean;
}>;

export default function LocationDetailsSection({
  title,
  children,
  isAccordionOpen = true,
}: LocationDetailsSectionProps): JSX.Element {
  const header = (
    <header className="text-brand-urbint-60 py-4">
      <h5 className="font-semibold">{title}</h5>
    </header>
  );

  return (
    <section>
      <Accordion header={header} isDefaultOpen={isAccordionOpen}>
        {children}
      </Accordion>
    </section>
  );
}
