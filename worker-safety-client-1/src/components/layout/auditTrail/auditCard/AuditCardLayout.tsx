import type { PropsWithChildren, ReactNode } from "react";

type AuditCardLayoutProps = PropsWithChildren<{ header: ReactNode }>;

function AuditCardLayout({ header, children }: AuditCardLayoutProps) {
  return (
    <div
      className="shadow-10 p-4 flex flex-col gap-y-3"
      data-testid="audit-card"
    >
      <div className="flex gap-x-6 gap-y-1 flex-wrap items-center text-neutral-shade-58 text-sm">
        {header}
      </div>
      <div>{children}</div>
    </div>
  );
}

export { AuditCardLayout };
