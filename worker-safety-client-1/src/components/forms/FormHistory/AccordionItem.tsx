import React, { useState } from "react";
import { Icon } from "@urbint/silica";

export function AccordionItem({
  title,
  children,
  className,
}: {
  title: React.ReactNode;
  children: React.ReactNode;
  level?: number;
  className?: string;
}) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div>
      <button
        className={`flex w-fit-content items-center justify-between gap-2 text-left`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className={className ?? `flex items-center`}>{title}</div>
        <Icon
          name="chevron_big_right"
          className={`transform transition-transform duration-200 ${
            isOpen ? "rotate-90" : ""
          }`}
        />
      </button>
      <div
        className={`overflow-hidden transition-all duration-200 ${
          isOpen ? "max-h-auto" : "max-h-0"
        }`}
      >
        <div>{children}</div>
      </div>
    </div>
  );
}

export default AccordionItem;
