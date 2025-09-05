import type { PropsWithChildren, ReactNode } from "react";
import type { UserRole } from "@/types/auth/AuthUser";
import { isSome } from "fp-ts/lib/Option";
import AdminAvatar from "@/components/shared/avatar/admin/AdminAvatar";
import InitialsAvatar from "@/components/shared/avatar/initials/InitialsAvatar";
import { AuditCardLayout } from "./AuditCardLayout";

type AuditCardHeaderProps = {
  avatar: ReactNode;
  name: string;
  timestamp: string;
  location?: { id: string; name: string } | string;
};

function AuditCardHeader({
  avatar,
  name,
  timestamp,
  location,
}: AuditCardHeaderProps) {
  return (
    <div className="flex gap-x-6 gap-y-1 flex-wrap items-center text-neutral-shade-58 text-sm">
      <div className="flex items-center text-neutral-shade-100 gap-2">
        {avatar}
        <span className="text-base">{name}</span>
      </div>
      <span>{timestamp}</span>
      {location && (
        <span>
          {typeof location === "string"
            ? location
            : "name" in location
            ? location.name
            : isSome(location)}
        </span>
      )}
    </div>
  );
}

type AuditCardProps = PropsWithChildren<{
  username?: string;
  userRole?: UserRole | string;
  timestamp: string;
  location?: { id: string; name: string } | string;
}>;

export default function AuditCard({
  username = "",
  userRole = "",
  timestamp,
  location,
  children,
}: AuditCardProps): JSX.Element {
  const adminAvatar = <AdminAvatar />;
  const initialsAvatar = <InitialsAvatar name={username} />;
  const [avatar, name] =
    userRole === "administrator"
      ? [adminAvatar, "Urbint Administrator"]
      : [initialsAvatar, username];

  const header = (
    <AuditCardHeader
      avatar={avatar}
      name={name}
      timestamp={timestamp}
      location={location}
    />
  );

  return <AuditCardLayout header={header}>{children}</AuditCardLayout>;
}
