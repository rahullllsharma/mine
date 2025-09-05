import type { HazardAggregator } from "@/types/project/HazardAggregator";
import type { SiteConditionAnalysisInputs } from "@/types/report/DailyReportInputs";
import JobReportCard from "../JobReportCard";
import { MarkAllControls } from "../markAllControls/MarkAllControls";

export type SiteConditionReportCardProps = {
  siteCondition: HazardAggregator;
  selectedSiteCondition?: SiteConditionAnalysisInputs;
  isCompleted?: boolean;
};

export default function SiteConditionReportCard({
  siteCondition,
  selectedSiteCondition,
  isCompleted,
}: SiteConditionReportCardProps): JSX.Element {
  const isMarkAllControlsVisible = !isCompleted;

  return (
    <JobReportCard
      job={siteCondition}
      selectedJob={selectedSiteCondition}
      switchLabel="Applicable?"
      formGroupKey="siteConditions"
      isCompleted={isCompleted}
    >
      {isMarkAllControlsVisible && (
        <MarkAllControls
          element={siteCondition}
          hazards={selectedSiteCondition?.hazards}
          formGroupKey="siteConditions"
        />
      )}
    </JobReportCard>
  );
}
