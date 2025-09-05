import { AvatarLoader } from "@/components/shared/avatar/loader/AvatarLoader";
import { AuditCardLayout } from "../AuditCardLayout";

function AuditCardLoader() {
  const header = (
    <div className="flex flex-1 items-center text-neutral-shade-100 gap-2">
      <AvatarLoader />
      <div className="flex flex-1 gap-4">
        <div className="h-2 bg-neutral-shade-18 rounded w-1/4" />
        <div className="h-2 bg-neutral-shade-18 rounded w-1/6" />
      </div>
    </div>
  );

  return (
    <AuditCardLayout header={header}>
      <div className="h-2 bg-neutral-shade-18 rounded" />
    </AuditCardLayout>
  );
}

export { AuditCardLoader };
