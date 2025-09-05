import type { AuditEvent } from "@/types/auditTrail/AuditEvent";
import { useQuery } from "@apollo/client";
import EmptyContent from "@/components/emptyContent/EmptyContent";
import AuditTrail from "@/components/layout/auditTrail/AuditTrail";
import ProjectAudits from "@/graphql/queries/projectAudits.gql";
import { AuditCardLoader } from "@/components/layout/auditTrail/auditCard/loader/AuditCardLoader";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

const ProjectAuditLoader = () => {
  return (
    <div className="flex flex-col gap-4">
      {[...Array(5)].map(value => (
        <AuditCardLoader key={value} />
      ))}
    </div>
  );
};

type ProjectAuditProps = {
  projectId: string;
};

export default function ProjectAudit({
  projectId,
}: ProjectAuditProps): JSX.Element {
  const { workPackage } = useTenantStore(state => state.getAllEntities());
  const { data, loading } = useQuery(ProjectAudits, {
    variables: {
      projectId,
    },
    fetchPolicy: "cache-and-network",
  });
  const audits: AuditEvent[] = data?.project.audits || [];

  const shouldShowEmptyState = audits.length === 0 && !loading;
  if (shouldShowEmptyState) {
    return (
      <div className="flex items-center min-h-[300px]">
        <EmptyContent
          title="You currently have no history"
          description={`An audit trail will appear here once updates are made to this ${workPackage.label.toLowerCase()}`}
        />
      </div>
    );
  }

  return (
    <>
      <div>
        <h6 className="leading-7">History</h6>
        <p className="text-neutral-shade-38 leading-5 text-sm">
          {`Monitor updates made to your ${workPackage.labelPlural.toLowerCase()} and ${workPackage.label.toLocaleLowerCase()} content`}
        </p>
      </div>
      <div className="mt-4">
        {loading ? (
          <ProjectAuditLoader />
        ) : (
          <AuditTrail auditEventsList={audits} />
        )}
      </div>
    </>
  );
}
