import type { Insight } from "@/types/insights/Insight";
import Link from "next/link";
import React from "react";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import ReportInsight from "../ReportInsight";

const EmptyInsightsText = ({ isAdmin }: { isAdmin: boolean }) =>
  isAdmin ? (
    <p>
      {`You don't have any insights added. Please add it in the
  "Insights" tab`}{" "}
      <Link href="/admin/config">
        <a className="underline text-brand-gray-80">here</a>
      </Link>
    </p>
  ) : (
    <p>
      Currently, no Insight reports have been configured. Please, contact your
      administrator to add if needed.
    </p>
  );

interface ReportInsightProps {
  insight?: Insight;
  embedData?: {
    embedUrl: string;
    reportId: string;
    id: string;
  };
  embedToken: string;
  visibleInsights: Insight[];
}
function InsightReportType({
  insight,
  embedData,
  embedToken,
  visibleInsights,
}: ReportInsightProps) {
  const { isAdmin } = useAuthStore();
  return (
    <>
      {insight ? (
        <ReportInsight
          insight={insight}
          embedData={embedData}
          embedToken={embedToken}
        />
      ) : visibleInsights.length ? (
        <p>There has been some error, please refresh.</p>
      ) : (
        <div>
          <EmptyInsightsText isAdmin={isAdmin()} />
        </div>
      )}
    </>
  );
}

export default InsightReportType;
