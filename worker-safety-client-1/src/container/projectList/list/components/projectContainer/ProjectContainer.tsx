import type { PropsWithChildren } from "react";
import Accordion from "@/components/shared/accordion/Accordion";

function ProjectContainer({
  title,
  children,
}: PropsWithChildren<{ title: string }>) {
  return (
    <Accordion
      header={
        <header className="text-brand-urbint-60 py-4">
          <h5 className="font-semibold">{title}</h5>
        </header>
      }
      isDefaultOpen
    >
      <div className="grid gap-4 grid-cols-auto-fill-list-card">{children}</div>
    </Accordion>
  );
}

export { ProjectContainer };
