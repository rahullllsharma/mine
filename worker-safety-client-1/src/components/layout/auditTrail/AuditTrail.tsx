import type { AuditEvent } from "@/types/auditTrail/AuditEvent";
import { AuditObjectType } from "@/types/auditTrail/AuditObjectType";
import { getFormattedDateTimeTimezone } from "@/utils/date/helper";
import AuditCard from "./auditCard/AuditCard";
import { getAuditCardContent, getDIRCardContent } from "./utils";

type AuditTrailProps = {
  auditEventsList: AuditEvent[];
};

export default function AuditTrail({
  auditEventsList,
}: AuditTrailProps): JSX.Element {
  return (
    <div className="flex flex-col gap-4">
      {auditEventsList.map((audit, index) => {
        let children;
        if (
          audit.objectType === AuditObjectType.TASK ||
          audit.objectType === AuditObjectType.SITE_CONDITION ||
          audit.objectType === AuditObjectType.PROJECT
        ) {
          children = getAuditCardContent(audit);
        } else if (audit.objectType === AuditObjectType.DAILY_REPORT) {
          children = getDIRCardContent(audit);
        }

        const timestamp = getFormattedDateTimeTimezone(audit.timestamp);

        if (!children) {
          return null;
        }
        return (
          <AuditCard
            username={audit.actor?.name}
            userRole={audit.actor?.role}
            timestamp={timestamp}
            location={audit.objectDetails?.location}
            key={index}
          >
            {children}
          </AuditCard>
        );
      })}
    </div>
  );
}
